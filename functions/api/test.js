export async function onRequest() {
  return new Response(JSON.stringify({ ok: true, test: "functions-work" }), {
    status: 200,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
  });
}
