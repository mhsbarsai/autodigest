// api/subscribe.js - Vercel Serverless Function
export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed. Use POST.' });
  }

  try {
    const { email } = req.body || {};

    if (!email || typeof email !== 'string') {
      return res.status(400).json({ error: 'Valid email address is required.' });
    }

    const cleanEmail = email.trim().toLowerCase();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(cleanEmail)) {
      return res.status(400).json({ error: 'Please enter a valid email format.' });
    }

    const apiKey = process.env.RESEND_API_KEY;
    if (!apiKey) {
      console.warn('RESEND_API_KEY environment variable is not configured.');
      // Return success simulation so subscriber UX is never broken if secret is still being set
      return res.status(200).json({ 
        success: true, 
        message: 'Registered successfully (pending activation).' 
      });
    }

    // 1. Try to add to Resend Contacts (Requires Full Access key)
    try {
      await fetch('https://api.resend.com/contacts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'User-Agent': 'Creavora/1.0',
        },
        body: JSON.stringify({
          email: cleanEmail,
          unsubscribed: false,
        }),
      });
    } catch (contactErr) {
      console.warn('Resend contact registration warning:', contactErr);
    }

    // 2. Dispatch Welcome Email to the new subscriber
    const fromEmail = process.env.RESEND_FROM_EMAIL || 'Creavora <onboarding@resend.dev>';
    
    const emailPayload = {
      from: fromEmail,
      to: [cleanEmail],
      subject: 'Welcome to Creavora — Your morning technical briefings start tomorrow',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Welcome to Creavora</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0c0e12; color: #f1f5f9; padding: 40px 16px; margin: 0;">
          <div style="max-width: 580px; margin: 0 auto; background-color: #12151c; border: 1px solid #1e2433; border-radius: 12px; padding: 36px 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
            <div style="border-bottom: 1px solid #1e2433; padding-bottom: 20px; margin-bottom: 24px;">
              <span style="font-size: 22px; font-weight: 700; letter-spacing: -0.5px; color: #ffffff;">Creavora</span>
              <span style="display: inline-block; font-size: 11px; background-color: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); padding: 2px 8px; border-radius: 12px; margin-left: 10px; font-weight: 600;">TECHNICAL INTELLIGENCE</span>
            </div>
            
            <h1 style="font-size: 24px; font-weight: 600; color: #ffffff; margin-top: 0; line-height: 1.3;">Welcome aboard.</h1>
            <p style="font-size: 15px; color: #94a3b8; line-height: 1.6;">
              You have been successfully added to <strong>Creavora</strong>. You will now receive our daily autonomous briefings straight to your inbox.
            </p>
            
            <div style="background-color: #181d28; border-left: 3px solid #6366f1; border-radius: 6px; padding: 18px; margin: 24px 0;">
              <div style="font-size: 14px; font-weight: 600; color: #ffffff; margin-bottom: 8px;">What to expect:</div>
              <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #cbd5e1; line-height: 1.7;">
                <li><strong>Timing:</strong> Every morning before <strong>06:00 WIB</strong>.</li>
                <li><strong>Format:</strong> 3-minute high-density read (frontier models, agent architectures, and tools).</li>
                <li><strong>Strict Filter:</strong> Zero marketing fluff, pure engineering signal.</li>
              </ul>
            </div>

            <p style="font-size: 14px; color: #94a3b8; line-height: 1.6;">
              If this landed in your Spam/Promotions folder, please drag this email to your Primary inbox so you don't miss tomorrow's edition.
            </p>

            <div style="border-top: 1px solid #1e2433; margin-top: 32px; padding-top: 20px; font-size: 12px; color: #64748b; line-height: 1.5;">
              Dispatched daily by Creavora Autonomous Pipeline &bull; <a href="https://www.creavora.my.id" style="color: #818cf8; text-decoration: none;">creavora.my.id</a>
            </div>
          </div>
        </body>
        </html>
      `,
    };

    const sendRes = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'Creavora/1.0',
      },
      body: JSON.stringify(emailPayload),
    });

    const sendData = await sendRes.json();
    if (!sendRes.ok) {
      console.warn('Welcome email delivery note:', sendData);
    }

    return res.status(200).json({
      success: true,
      message: 'Successfully subscribed to Creavora.',
    });
  } catch (err) {
    console.error('Subscription handler error:', err);
    return res.status(500).json({ error: 'Server error processing subscription.' });
  }
}
