---
name: larch-story-studio
description: Complete Larch authoring Skill for projects, boards, story cards, characters, media, asset packs, AI generation, versions, restore, and export through the authenticated Larch MCP server at larch.ink.
---

# Larch Story Studio — complete operating Skill

This is the only Larch Skill and operating guide needed. Install or enable it with the current AI host's supported Skill/MCP workflow. Do not ask the user for another setup prompt, platform-specific variant, or repeated connection details.

## Connection

- Canonical Larch site: `https://larch.ink`. Use this exact host for production MCP and REST connections; do not substitute an alias or legacy domain.
- Transport: Streamable HTTP MCP
- MCP URL: `https://larch.ink/mcp`
- Authorization header: `Bearer <LARCH_API_KEY>` (configured in host MCP config or read from `~/.config/larch/key`)
- REST base URL: `https://larch.ink`
- REST authorization: `Authorization: Bearer <LARCH_API_KEY>`

Treat the bearer value as a secret. Keep it only in the host's protected MCP/Skill configuration or request header. Never write it into a project, card, character, media record, exported file, source repository, log, or chat reply. If the host cannot register remote MCP, use the REST fallback below immediately with the same bearer value; the user does not need to provide anything else.

## ID-first routing

Whenever the user provides a Larch ID without its full context, call `larch_resolve_id` first. It identifies project, board, character, project media, or account asset-pack IDs and returns the parent `projectId` when needed. Do not guess the ID type, search by visual similarity, or ask which kind it is unless the resolver returns multiple matches. Once exactly one match is found, continue automatically.

Examples:

- Project ID → read with `larch_get_project`.
- Board ID → use the returned `projectId`, then `larch_get_board`; pass both IDs to every board/card mutation.
- Character ID → use the returned `projectId`, then `larch_list_characters` or the character tools.
- Media ID → use the returned `projectId`, then `larch_upsert_media` or `larch_delete_media`.
- Asset Pack ID → `larch_get_asset_pack`, then update the full pack with `larch_upsert_asset_pack`.

## Required workflow

1. Resolve a supplied ID. If no ID was supplied, use the Starting context or call `larch_list_projects`.
2. Read the latest target before changing it: project, board, character list, media, or complete asset pack. Never edit from memory or from an earlier conversation snapshot.
3. Make the smallest focused mutation that satisfies the request. Preserve unknown fields and every item not named by the user.
4. Give every mutation a concise, specific Traditional-Chinese `summary`; it becomes the audit/version label.
5. Read the changed target again and verify IDs, links, counts, and requested fields. For large project edits, call `larch_list_versions` to confirm the automatic snapshot exists.
6. **Look at what you made.** Any change a player would see — dialogue, choices, art, backgrounds, characters, stage layout, effects — is only verified once you have opened the preview described below and actually looked at the rendered frame. Reading the JSON back is not looking.
7. Report the result briefly. Do not expose the bearer key.

## Seeing the rendered result — no login required

`larch_preview_project(projectId, boardId?, cardId?, hours?)` returns short-lived URLs that need no Google account: the Agent Key you already hold is the permission. Open them with whatever browser tool your host gives you (browser/computer use, a screenshot tool, a headless fetch of the page) and look at the frame.

- `url` / `playUrl`: the story plays from its start card, exactly as a player sees it.
- `cardId`: plays only that one card — the fastest way to check a card you just edited.
- `boardUrl`: the whole board as a zoomable map, for checking structure and routing instead of art.

The link reads the project as it is right now, so a reload after another edit shows the new version — do not mint a new link for every change. It expires (24 hours by default, `hours` up to 168), it is read-only, and it dies the moment this Agent Key is disabled or revoked. Treat it as private: it is not the link you hand to players.

If your host genuinely cannot open a URL, say so instead of claiming the result looks right.

## Complete MCP tool map

Discovery and projects:

- `larch_resolve_id(id)`: resolve any pasted Larch ID.
- `larch_list_projects()`: list accessible projects.
- `larch_create_project(...)`: create a project.
- `larch_get_project(projectId)`: returns `{ project, revision }` with the complete project data.
- `larch_update_interface(projectId, surface, html, enabled, expectedHtml, summary)`: update only the title or dialogue Skills interface. Read settings.customInterfaces first; pass its previous HTML as expectedHtml (empty if absent). The server preserves a complete recovery before writing.
- `larch_replace_project(projectId, project, expectedRevision, summary)`: replace a whole project only when a focused tool cannot express the requested change; stale revisions are rejected.

Boards and story cards:

- `larch_list_boards(projectId)`, `larch_get_board(projectId, boardId)`; board reads return a revision.
- `larch_upsert_board(...)`: create or patch board metadata; optional `nodes` and `edges` are complete replacements and require the latest `expectedRevision`.
- `larch_delete_board(...)`: destructive; only on explicit request. A project must retain one board.
- `larch_patch_node(projectId, boardId, nodeId, patch, expectedRevision, summary)`: safely patch one existing card after reading the latest board.
- `larch_upsert_nodes(projectId, boardId, nodes, edges?, expectedRevision?, summary)`: create cards or apply an intentional batch on exactly one board.
- `larch_delete_nodes(projectId, boardId, nodeIds, summary)`: destructive; only on explicit request.
- `larch_generate_story(projectId, boardId?, prompt, afterNodeId?)`: generate and insert story cards only when the user asks for AI generation.

Project media and art — **generate images with your own image tool**:

- Draw backgrounds, props and character variants with the image generator your host gives you (Codex Image Gen or equivalent), then upload the PNG with `larch_upload_media(...)` and use the returned `asset.url`. This is the supported path: no Larch AI credits, no dependency on Larch's upstream image provider.
- `larch_upload_media(...)`: upload base64 image/audio/video/document and attach it to the project.
- `larch_upsert_media(projectId, assets, summary)`: add or patch media records by Media ID.
- `larch_delete_media(projectId, assetIds, summary)`: destructive; removing a library record does not rewrite card URLs.
- `larch_generate_image(...)`: fallback for hosts with no image tool. Consumes credits and is rate limited; Muse Link returns 503 without automatic fallback when offline.

Voice and dialogue:

- `larch_list_voices(...)`: search the current system catalogue and the author's existing custom voices by language, tone and descriptive traits. Read the character profile and surrounding dialogue first.
- Keep one base `voiceId` per character so the character does not change voices between moods. Use line-level `emotion` for happy, sad, angry, fearful, surprised, disgusted, calm, whisper or fluent delivery.
- `larch_generate_voice(projectId, boardId?, nodeId, lineIndex?, voiceId, emotion?, rememberForCharacter?, summary)`: reads the current text, synthesizes it, writes the result to that line's `voiceUrl`, saves an audio asset in project media and normally remembers the selected voice on the speaking character. It consumes voice credits and requires `ai`, `write` and `media` scopes.
- Generate speech only when the user asks. For multiple lines, call once per line with a stable character voice, then read the changed card and preview it with audio enabled.

### Transparent art: ask for real alpha, check it, then upload

Portraits, expression / outfit / pose variants, props, and anything that sits on top of a scene must reach Larch as a genuinely transparent PNG — a real alpha channel, not a checkerboard painted into the RGB.

1. Ask your image tool for the transparent background directly and keep the alpha it returns. Codex's built-in `image_gen` does this natively; on the OpenAI Images API it is `background: "transparent"` with `output_format: "png"` (`jpeg` cannot carry alpha). Still prompt for the subject alone: no cast shadow, no ground plane, no vignette, nothing touching the frame edge.
2. Check the file before uploading, because native transparency is new and still leaves marks: all four corners fully transparent, hair strands / glasses / straps intact, no grey or coloured halo around the silhouette, and no subject pixels stuck a few steps short of opaque (alpha 252–254). Flatten that near-opaque alpha and despill the rim instead of shipping it; regenerate if the halo is baked into the colour.
3. Only when the host's image tool cannot emit alpha at all, fall back to keying: generate the subject on one flat, evenly lit chroma backdrop (`#00B140`, or `#FF00FF` for green subjects), then cut it out locally — `magick raw.png -alpha set -fuzz 12% -fill none -draw "alpha 0,0 floodfill" -channel A -blur 0x0.6 -level 45%,55% +channel cutout.png` — flood-filling inward from the corners so eye whites and same-coloured details inside the silhouette survive.
4. Upload the finished transparent PNG with `larch_upload_media` and use the returned `asset.url`. Never attach an opaque or backdrop-coloured version to a character, card, or pack.

Keep one character's whole set on the same route and the same framing, so the base portrait and every variant stay aligned. Scene backgrounds are the exception: they are full-frame art and need no transparency.

Characters:

- `larch_list_characters(projectId)`: always obtain the current `characterId` and available expressions first.
- `larch_upsert_character(...)`: create a character or patch only supplied profile fields. Pass `expressions` — `{ name, imageUrl, emotion?, prompt?, kind? }`, up to 24 — to attach expression / outfit / pose art you generated with a transparent background and uploaded yourself. A matching `id`, or matching `name` + `kind`, replaces that variant instead of duplicating it. Only variants in the expression set appear in the dialogue editor's emotion picker.
- `larch_delete_character(...)`: destructive; only on explicit request.
- `larch_generate_character_art(projectId, characterId, kind, variants)`: fallback generator for up to 8 expression, outfit, or pose variants. The character needs `portraitUrl`. Successful variants are written to both the expression set and project media; inspect per-variant `failures`.

Account asset packs:

- `larch_list_asset_packs()`, `larch_get_asset_pack(packId)`.
- `larch_upsert_asset_pack(...)`: creates or replaces a personal pack. `assets` is the complete list, so read first and merge locally; never drop unmentioned assets.
- `larch_delete_asset_pack(packId, summary)`: permanent and destructive; only on explicit request after confirming the ID.

Versions and export:

- `larch_list_versions(projectId)`.
- `larch_restore_version(projectId, versionId)`: only for an explicit rollback or a confirmed broken edit.
- `larch_export_project(projectId, boardId?)`: export the whole project or one board for Unity/Web.

Preview:

- `larch_preview_project(projectId, boardId?, cardId?, hours?)`: no-login URLs for looking at the rendered result. See the section above.

Publishing — outward facing, explicit request only:

- `larch_list_published()`: this account's marketplace listings with views, plays, likes and unanswered comments. Call it first to know whether a project is already listed.
- `larch_publish_game(projectId, title?, description?, coverUrl?, tags?, remixable?, version?, updateNote?, aiDisclosure?)`: lists the project on the marketplace, or — when it is already listed — republishes it so players get the current board. One project has exactly one listing, so "上架" and "更新版本" are the same call. Omitted fields keep the previous listing's values. Preview the game first; a broken route reaches real players.
  - `version` and `updateNote` (the release note, ≤2000 chars) go in the same call; do not reach for `larch_upsert_release_note`, that one is Larch's own site changelog and admin-only.
  - The first publish of a project is refused until `aiDisclosure` is set. It is an object, `{"mode":"heavy"}` for heavy use (the format other listings already carry). Ask the user what to disclose, never guess. The MCP tool schema some clients cache omits this field and sends it as a string, which fails validation; in that case call `tools/call` over raw JSON-RPC to `https://larch.ink/mcp` (Bearer key, `initialize` first, ~30s per call).
  - Every call is a new release (`releaseNumber` +1) even with the same version. Run it exactly once; never re-run a publish script to "check".
  - To change only the store page (description, cover, remix, AI disclosure, screenshots) without a new version or follower notification, use the tool/button for "only update store info" instead of republishing.
- `larch_unpublish_game(projectId)`: removes the listing. Player links break and the listing's stats are gone for good.
- `larch_share_link(projectId, permission)`: a durable public `/play` URL (and read-only `/share` board URL) to hand to other people. Calling it again refreshes the same URL with the current project. This is not the preview link.

Official site content — admin accounts only:

- `larch_list_release_notes()`: every changelog entry on `/changelog`, drafts included.
- `larch_upsert_release_note(id?, version, title, summary, cover?, markdown, status, releasedAt)`: write or edit one. `markdown` is the body: headings, lists, quotes, `![](url)` images and `@[video](url)` embeds all convert to the same document blocks the admin editor produces. Leave `status` at `draft` and only send `published` when the user explicitly says to publish it.
- `larch_list_wiki_articles()` and `larch_upsert_wiki_article(id?, title, slug?, category?, tags?, excerpt?, cover?, markdown, status, order?)`: the official Wiki at `/wiki`, same Markdown body and the same draft-first rule.

## Content and data rules

- A playable board has exactly one card with `data.start=true`.
- Supported card types: `dialogue`, `choice`, `event`, `scene`, `input`, `aiDialogue`, `aiStory`, `miniGame`, `setVariable`, `boardJump`, and `group`.
- `aiStory` is a web-only card the AI director improvises at playback: give it `aiPrompt`, `aiStoryExitConditions` (any one ends the segment), `aiStoryMaxTurns`, and `aiStoryScope` (`board` / `library` / `selected` with `aiStoryAssets`). It spends AI credits per beat and Unity exports skip it.
- A `setVariable` card carries `data.variableOps`: an array of `{ id, variable, kind, value?, valueFrom?, min?, max? }` where `kind` is `set` | `add` | `toggle` | `random`. It applies on entry, before outgoing edge conditions, and plays silently when `data.text` is empty. Every `variable` must match a `project.variables[].name`.
- Keep stable IDs when updating. New IDs should be descriptive and unique.
- A source handle connects to at most one target; the server keeps the newest edge.
- Choices and board jumps must point to valid targets. Verify every referenced node and Board ID.
- Write player-facing copy in the project's locale; default to Traditional Chinese when unspecified.
- Reuse existing characters, backgrounds, BGM, and pack assets before generating replacements. When something really is missing, draw it with your own image generator as a transparent PNG, as described above, and upload it instead of spending Larch AI credits.
- Do not rewrite or delete author-created content unless requested. Never change project settings, languages, credentials, billing, or access controls unless the user explicitly asks and a dedicated tool supports it.
- Mutations are versioned, but destructive operations still require an explicit user request.

## REST fallback

Use JSON and the bearer header (or `~/.config/larch/key`):

- `GET /api/agent/resolve/:id`
- `GET|POST /api/agent/projects`
- `GET|PUT /api/agent/projects/:projectId`; GET returns an ETag and full-project PUT requires it in `If-Match`
- `PUT /api/agent/projects/:projectId/interface` with surface (title/dialogue), html, enabled, expectedHtml and summary
- `GET /api/agent/projects/:projectId/boards`
- `GET|PUT|DELETE /api/agent/projects/:projectId/boards/:boardId`; PUT requires the latest ETag in `If-Match`
- `GET|PATCH /api/agent/projects/:projectId/boards/:boardId/nodes/:nodeId`; PATCH requires the latest ETag in `If-Match`
- `POST|DELETE /api/agent/projects/:projectId/nodes` with optional `boardId`
- `POST /api/agent/projects/:projectId/story/generate` with optional `boardId`
- `GET /api/agent/voices?language=&tone=&query=&includeCustom=&offset=&limit=`
- `POST /api/agent/projects/:projectId/voice/generate` with `nodeId`, optional `lineIndex`, selected `voiceId`, optional `emotion` and `rememberForCharacter`
- `POST /api/agent/projects/:projectId/images/generate`
- `POST|PUT|DELETE /api/agent/projects/:projectId/media`
- `GET|POST /api/agent/projects/:projectId/characters`
- `DELETE /api/agent/projects/:projectId/characters/:characterId`
- `POST /api/agent/projects/:projectId/characters/:characterId/art`
- `GET /api/agent/asset-packs`
- `GET|PUT|DELETE /api/agent/asset-packs/:packId`
- `GET /api/agent/projects/:projectId/versions`
- `POST /api/agent/projects/:projectId/versions/:versionId/restore`
- `GET /api/agent/projects/:projectId/export?boardId=:boardId`
- `GET /api/agent/projects/:projectId/preview?boardId=&cardId=&hours=`
- `GET /api/agent/published`
- `POST|DELETE /api/agent/projects/:projectId/publish`
- `POST /api/agent/projects/:projectId/share-link`
- `GET|POST /api/agent/release-notes` and `PATCH /api/agent/release-notes/:id` (admin accounts only)
- `GET|POST /api/agent/wiki` and `PATCH /api/agent/wiki/:id` (admin accounts only)

## Permissions

The key carries a scope list the account owner controls in Larch's **AI 輔助** settings page. `read` / `write` / `media` / `ai` / `export` / `versions` cover authoring; `preview` allows the no-login preview links; `publish` covers the marketplace, share links and release notes. A 403 saying a scope is missing is a deliberate setting, not a bug — tell the user which switch to turn on in that page rather than working around it.
