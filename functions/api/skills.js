// Cloudflare Pages Function: /api/skills
// Returns all available skills from skills.json

export async function onRequest(context) {
  try {
    // Fetch skills data from public folder
    const response = await fetch(new URL('/skills.json', context.request.url));
    const skills = await response.json();
    
    return new Response(JSON.stringify(skills), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'max-age=300'
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({ 
      error: 'Failed to load skills',
      message: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
