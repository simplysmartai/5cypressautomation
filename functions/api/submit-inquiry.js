export async function onRequest(context) {
  try {
    const { request, env } = context;

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    const formData = await request.formData();
    const name = formData.get("name");
    const email = formData.get("email");
    const company = formData.get("company");
    const message = formData.get("message");
    const budget = formData.get("budget");

    if (!name || !email) {
      return new Response("Missing required fields", { status: 400 });
    }

    // Prepare email content
    const emailSubject = `New Automation Inquiry: ${name} from ${company}`;
    const emailBody = `
      <h1>New Project Inquiry</h1>
      <p><strong>Name:</strong> ${name}</p>
      <p><strong>Email:</strong> ${email}</p>
      <p><strong>Company:</strong> ${company || "Not provided"}</p>
      <p><strong>Estimated Budget:</strong> ${budget || "Not provided"}</p>
      <hr>
      <h3>Project Details:</h3>
      <p>${message}</p>
    `;

    // Send email using Resend (assuming RESEND_API_KEY is an env var)
    // If running on Cloudflare Pages, we need to use the fetch API directly.
    // Assuming Resend API key is available as env.RESEND_API_KEY
    if (env.RESEND_API_KEY) {
        const resendResponse = await fetch("https://api.resend.com/emails", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${env.RESEND_API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                from: "Simply Smart Automation <onboarding@resend.dev>", // Or verified domain
                to: ["info@5cypress.com"],
                subject: emailSubject,
                html: emailBody,
                reply_to: email
            })
        });

        if (!resendResponse.ok) {
            const errorText = await resendResponse.text();
            console.error("Resend API Error:", errorText);
             // Fallback or just log, but let the user know submission "succeeded" if crucial
            return new Response(JSON.stringify({ success: false, error: "Email service error" }), {
                headers: { "Content-Type": "application/json" },
                status: 500
            });
        }
    } else {
        // Fallback or dev mode log
        console.log("Mock Email Sent:", { emailSubject, emailBody });
         return new Response(JSON.stringify({ success: true, message: "Form submitted (Mock Mode)" }), {
            headers: { "Content-Type": "application/json" },
            status: 200
        });
    }

    return new Response(JSON.stringify({ success: true, message: "Inquiry received" }), {
      headers: { "Content-Type": "application/json" },
      status: 200
    });

  } catch (err) {
    console.error(err);
    return new Response(JSON.stringify({ error: "Server Error" }), {
      headers: { "Content-Type": "application/json" },
      status: 500
    });
  }
}
