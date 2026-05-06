import { Hono } from "hono";
import { basicAuth } from "hono/basic-auth";
import decryptedJson from "../../generated/decrypted.json" with {
  type: "json",
};
import decryptedLatestJson from "../../generated/decryptedlatest.json" with {
  type: "json",
};
import tweakedJson from "../../generated/tweaked.json" with { type: "json" };
import tweakedLatestJson from "../../generated/tweakedlatest.json" with {
  type: "json",
};

const app = new Hono<{ Bindings: CloudflareBindings }>();

app.use(
  "/*",
  // Basic Auth Middleware
  async (c, next) => {
    if (!c.env.WORKER_USERNAME || !c.env.WORKER_PASSWORD) {
      console.error(
        "WEB_USERNAME or WEB_PASSWORD is not set in Cloudflare environment",
      );
      return c.json({ error: "Server configuration error" }, 500);
    }
    const auth = basicAuth({
      username: c.env.WORKER_USERNAME,
      password: c.env.WORKER_PASSWORD,
    });
    return await auth(c, next);
  },
);

app.get("/tweaked.json", (c) => {
  return c.json(tweakedJson);
});

app.get("/tweakedlatest.json", (c) => {
  return c.json(tweakedLatestJson);
});

app.get("/decrypted.json", (c) => {
  return c.json(decryptedJson);
});

app.get("/decryptedlatest.json", (c) => {
  return c.json(decryptedLatestJson);
});

app.get("/download/:owner/:repo/:asset_id/:name?", async (c) => {
  const { owner, repo, asset_id } = c.req.param();
  const token = c.env.WORKER_GITHUB_TOKEN;

  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/releases/assets/${asset_id}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/octet-stream",
        "User-Agent": "Cloudflare-Worker",
      },
      redirect: "manual",
    },
  );

  const location = response.headers.get("Location");
  if (location) {
    return c.redirect(location, 302);
  }
});

export default app;
