// Cloudflare Function for Form Submission
// Handles validation and email forwarding via Resend

export async function onRequestPost({ request, env }) {
  try {
    // 1. Get Form Data
    const data = await request.json();
    const { name, email, company, timeline, details } = data;

    // 2. Validate Input
    if (!name || !email) {
      return new Response(JSON.stringify({ error: "Name and Email are required." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    // 3. Construct Email Payload
    const emailSubject = `New Automation Inquiry: ${name} from ${company || 'Unknown'}`;
    const emailHtml = `
      <div style="font-family: sans-serif; color: #333;">
        <h2 style="color: #4CAF50;">New Automation Inquiry</h2>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Company:</strong> ${company || 'Not provided'}</p>
        <p><strong>Timeline:</strong> ${timeline || 'Not provided'}</p>
        <hr style="border: 0; border-top: 1px solid #eee;">
        <h3>Project Details:</h3>
        <p style="white-space: pre-wrap;">${details || 'No details provided.'}</p>
        <br>
        <p style="font-size: 0.8em; color: #888;">Sent from 5cypress.com Vetting Form</p>
      </div>
    `;

    // 4. Send Email via Resend
    // Requires RESEND_API_KEY secret to be set in Cloudflare Pages settings
    if (env.RESEND_API_KEY) {
      const resendResponse = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.RESEND_API_KEY}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          from: "5 Cypress System <onboarding@resend.dev>", // Or verified domain sender
          to: "info@5cypress.com",
          reply_to: email,
          subject: emailSubject,
          html: emailHtml
        })
      });

      if (!resendResponse.ok) {
        const errorText = await resendResponse.text();
        console.error("Resend API Error:", errorText);
        throw new Error("Failed to deliver email.");
      }
    } else {
      console.log("MOCK SEND (Missing API Key):", { emailSubject });
    }

    // 5. Success Response
    return new Response(JSON.stringify({ success: true, message: "Inquiry received. We will be in touch shortly." }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });

  } catch (err) {
    console.error("Form Submission Error:", err);
    return new Response(JSON.stringify({ error: "Internal Server Error. Please contact info@5cypress.com directly." }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
