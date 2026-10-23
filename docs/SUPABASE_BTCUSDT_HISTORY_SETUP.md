# Supabase persistence setup for BTCUSDT history

This repository now has an optional Supabase Storage persistence path. It is not active until the owner configures a Supabase project and GitHub Actions secrets.

## What is stored where

- **Private Supabase Storage bucket:** original monthly ZIP archives, checksum sidecars, collector manifest and reports.
- **Supabase Postgres table `public.btcusdt_history_objects`:** object path, dataset/month tags, byte size and SHA-256 catalog.
- **GitHub Actions artifact:** secondary temporary copy, currently retained for 30 days.

Do not insert millions of 1-minute candles as individual Postgres rows for this initial archive workflow. Keep raw archives as objects and query normalized Parquet/CSV derivatives only when needed. The free plan has finite storage/egress quotas; measure archive size during the canary before attempting the entire history range. A full 2017-present archive may exceed the free storage quota, in which case stop rather than silently dropping data or incurring charges.

## One-time owner setup

1. Create a Supabase project on the plan you intend to use.
2. In **Storage**, create a **private** bucket named `btc-usdt-history` (or set repository variable `SUPABASE_BUCKET` to the chosen name).
3. Open the Supabase SQL Editor and run `docs/supabase_btcusdt_history_schema.sql`.
4. In GitHub repository **Settings → Secrets and variables → Actions**, add:
   - Secret `SUPABASE_URL`: project URL, for example `https://YOUR_PROJECT_REF.supabase.co`.
   - Secret `SUPABASE_SERVICE_ROLE_KEY`: the service-role secret from the project's API settings. Treat it like a password; never commit or paste it into chat.
   - Optional repository variable `SUPABASE_BUCKET`: defaults to `btc-usdt-history`.
5. Run **Actions → BTCUSDT full historical archive collection** first for a one-month canary (for example `2026-09` to `2026-09`). Confirm the job reports uploads and verify the object count/bytes in Storage and catalog rows in Postgres.
6. Only after the canary passes and quota headroom is confirmed, run date ranges in bounded batches. Keep the generated manifest and checksum sidecars.

## Safety and failure behavior

- The uploader sends objects to the private bucket and upserts the metadata catalog using the service-role key.
- If the two required secrets are missing, the workflow explicitly skips cloud upload and still preserves the temporary GitHub artifact. This is not a successful durable backup.
- Upload errors stop the uploader and fail the upload step; the temporary artifact is still attempted.
- Do not change the bucket to public. Do not use a database password or service-role key as a workflow variable; use GitHub Secrets.
- GitHub Actions workflows added only on a feature branch may not be manually dispatchable until the workflow exists on the default branch. Do not merge the existing research PR just to bypass this requirement without reviewing it first.
