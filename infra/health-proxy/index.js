// Winziger Proxy-Worker fuer UptimeRobot: Render.com liegt hinter Renders eigener
// Cloudflare-Zone, die bekannte Monitoring-Bot-IPs/User-Agents (u.a. UptimeRobot)
// blockt -- ein direkter Health-Check von UptimeRobot auf die Render-URL zeigt
// deshalb faelschlich "down", obwohl der Service laeuft (siehe TODO.md/PROGRESS.md).
//
// Dieser Worker ruft das Render-/health-Endpoint stattdessen serverseitig aus
// Cloudflares eigenem Netzwerk ab -- dieser Request traegt keinen der bekannten
// Monitoring-Bot-Signaturen und wird deshalb nicht geblockt. UptimeRobot prueft
// diesen Worker statt direkt Render.
export default {
  async fetch(request, env) {
    try {
      const upstream = await fetch(env.UPSTREAM_HEALTH_URL, {
        cf: { cacheTtl: 0 },
      });
      const body = await upstream.text();
      return new Response(body, {
        status: upstream.status,
        headers: { "content-type": upstream.headers.get("content-type") || "application/json" },
      });
    } catch (err) {
      return new Response(JSON.stringify({ status: "error", detail: String(err) }), {
        status: 502,
        headers: { "content-type": "application/json" },
      });
    }
  },
};
