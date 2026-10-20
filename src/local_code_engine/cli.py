import argparse
import json
import os
import sys

from .benchmark import run_benchmark, save_results
from .controller import GenerationController, GenerationRequest
from .ollama_backend import OllamaBackend
from .verify import check_python_syntax


def main():
    parser = argparse.ArgumentParser(prog="local-code-engine")
    parser.add_argument("--host", default=None)

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health")

    gen = sub.add_parser("generate")
    gen.add_argument("prompt")
    gen.add_argument("--model", default="qwen2.5-coder:1.5b")
    gen.add_argument("--max-tokens", type=int, default=256)

    bench = sub.add_parser("benchmark")
    bench.add_argument("--model", default="qwen2.5-coder:1.5b")
    bench.add_argument("--runs", type=int, default=5)
    bench.add_argument("--max-tokens", type=int, default=256)
    bench.add_argument("--no-warmup", action="store_true")
    bench.add_argument(
        "--output", default="results/benchmark-results.json"
    )

    verify = sub.add_parser("verify")
    verify.add_argument("--file", required=True)

    args = parser.parse_args()
    host = args.host or os.getenv(
        "OLLAMA_HOST", "http://127.0.0.1:11434"
    )
    backend = OllamaBackend(host)
    controller = GenerationController(backend)

    try:
        if args.command == "health":
            data = backend.health()
            print(json.dumps({
                "ok": True,
                "host": host,
                "models": [
                    item.get("name")
                    for item in data.get("models", [])
                ],
            }, indent=2))

        elif args.command == "generate":
            result = controller.generate(
                GenerationRequest(
                    args.prompt, args.model, args.max_tokens
                )
            )
            print(result.response)
            print(
                f"\n[Throughput: {result.tokens_per_second:.2f} tokens/sec]",
                file=sys.stderr,
            )

        elif args.command == "benchmark":
            results = run_benchmark(
                controller,
                model=args.model,
                runs=args.runs,
                max_tokens=args.max_tokens,
                warmup=not args.no_warmup,
            )
            save_results(results, args.output)
            print(json.dumps(results["summary"], indent=2))
            print(f"Saved full results to {args.output}")

        elif args.command == "verify":
            result = check_python_syntax(args.file)
            print(json.dumps(result, indent=2))
            return 0 if result["ok"] else 1

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
