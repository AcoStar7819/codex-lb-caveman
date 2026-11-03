# Caveman integration context

## Purpose and usage

Enable **Caveman (Less token usage)** in an API key's **Limits** section. The flag is off for all existing and newly created keys. It adds compact answer guidance and encodes suitable JSON tool results with the official Caveman TOON encoder. For example, a uniform list of records with repeated `record_id`, `record_status` and `department` keys becomes a shared field header followed by rows. Every typed value is checked by decoding before the replacement is accepted.

## Deployment decision

The user requested one Docker container on Ubuntu, with no client setup. The Docker build includes `caveman-engine` from upstream revision `2e068f735253cce28256744804785f01887d9646`, with license and notice files. Python starts and reaps stateless encoder/decoder processes when needed. There is no always-running second HTTP proxy, new port, cloud account, telemetry upload or extra volume. Updating requires rebuilding the image with these sources; the running VDS has not been changed by this implementation.

Non-Docker installations need `caveman-engine` on PATH for input compression. Without it, concise-answer guidance still applies and context remains unchanged, with a content-free `caveman_projection_unavailable` warning.

## Why not the Python SDK middleware

Research covered [SDKs](https://docs.caveman.so/caveman/sdks-and-packages), [middleware](https://docs.caveman.so/caveman/middleware), and [TOON](https://docs.caveman.so/caveman/toon-and-pixel), checked against upstream source. The SDK is a client, not an embedded compression engine. `Cave.compress` needs a connected endpoint and uses blocking I/O; middleware needs an actual tool executor for recovery. Caveman's standalone proxy implements internal recovery for non-streaming requests, but cannot execute that loop on streams and has no WebSocket transport. Installing a schema-only recovery tool would send unusable calls to Codex. A Python adapter to the official stateless Engine meets the deployment requirement without inventing recovery support or adding an unused SDK dependency.

## Eligibility and failure modes

Only complete JSON arrays of at least two objects with identical ordered fields and scalar values are eligible. Inputs smaller than 512 characters, larger than 256 KiB, duplicate keys, nested values, non-finite numbers and unsafe large numbers are skipped. Up to eight segments per request are considered, with four simultaneous engine operations per worker and a two-second projection deadline. Tool call arguments, tool definitions, user/system text, code, images, and opaque reasoning are left alone. The original caller-owned history is never modified.

The encoded representation must be smaller including its format marker and decode to the original typed values. This preserves data semantics, not original JSON whitespace or lexical spelling. A consumer requiring literal byte-for-byte tool text should leave Caveman disabled. Engine failure or timeout retains the original context. Cancellation terminates and awaits the request's child process. No customer content or credentials are logged or persisted by this adapter.

## Savings and compatibility

Answer guidance preserves requested language, correctness, code and structured output. It does not lower reasoning effort or impose an output-token cap. HTTP/SSE, Chat conversion, compact and WebSocket request preparation share the policy; non-inference endpoints such as models, usage and file transfer are unchanged. Provider-reported usage remains the accounting source. Shorter representations do not guarantee lower billed usage: instruction overhead, tokenizer choice, model behavior and prompt cache effects matter. Enabling/disabling the option changes the prompt prefix and can invalidate a previously warm cache.
