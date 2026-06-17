# Examples

Small Magireco source JSON samples copied from the `external/magireco-source`
submodule for demos that should work without access to the full source repo.

Run a single-file translation:

```bash
uv run python -m mgrc_ai_trans trans-single examples/magireco-source/000003-3.json --special-fp examples/special_latest.json --model deepseek-v4-flash --tgt-root output/demo --log-root log/demo
```

Use `--model kimi-k2.6` to route the same request through Moonshot.
