import { Webhook } from 'svix';
import { headers } from 'next/headers';
import { NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/supabase';

export async function POST(req: Request) {
  const WEBHOOK_SECRET = process.env.CLERK_WEBHOOK_SECRET;
  if (!WEBHOOK_SECRET) {
    return NextResponse.json({ error: 'No webhook secret configured' }, { status: 500 });
  }

  // Get the headers
  const headerPayload = await headers();
  const svix_id = headerPayload.get('svix-id');
  const svix_timestamp = headerPayload.get('svix-timestamp');
  const svix_signature = headerPayload.get('svix-signature');

  if (!svix_id || !svix_timestamp || !svix_signature) {
    return NextResponse.json({ error: 'Missing svix headers' }, { status: 400 });
  }

  const payload = await req.json();
  const body = JSON.stringify(payload);

  // Verify the webhook signature
  const wh = new Webhook(WEBHOOK_SECRET);
  let evt: { type: string; data: { id: string; email_addresses: Array<{ email_address: string }>; first_name?: string; last_name?: string } };

  try {
    evt = wh.verify(body, {
      'svix-id': svix_id,
      'svix-timestamp': svix_timestamp,
      'svix-signature': svix_signature,
    }) as typeof evt;
  } catch (err) {
    console.error('Webhook signature verification failed:', err);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  const { type, data } = evt;

  if (type === 'user.created' || type === 'user.updated') {
    const { id, email_addresses, first_name, last_name } = data;
    const email = email_addresses?.[0]?.email_address ?? null;
    const full_name = [first_name, last_name].filter(Boolean).join(' ') || null;

    const { error } = await supabaseAdmin.from('profiles').upsert(
      { id, email, full_name },
      { onConflict: 'id' }
    );

    if (error) {
      console.error('Supabase upsert error:', error);
      return NextResponse.json({ error: 'DB error' }, { status: 500 });
    }
  }

  if (type === 'user.deleted') {
    const { id } = data;
    await supabaseAdmin.from('profiles').delete().eq('id', id);
  }

  return NextResponse.json({ success: true });
}
