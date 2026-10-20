import argparse
import json
import os
import sys

from .benchmark import run_benchmark, save_results
from .controller import GenerationController, GenerationRequest
from .llama_cpp_backend import LlamaCppBackend
from .ollama_backend import OllamaBackend
from .repair import repair_code
from .verify import check_python_syntax


def main():
    parser = argparse.ArgumentParser(prog="local-code-engine")
    parser.add_argument(
        "--backend",
        choices=["ollama", "llama.cpp"],
        default=os.getenv("LOCAL_CODE_ENGINE_BACKEND", "ollama"),
    )
    parser.add_argument("--host")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health")

    gen = sub.add_parser("generate")
    gen.add_argument("prompt")
    gen.add_argument("--model")
    gen.add_argument("--max-tokens", type=int, default=256)

    bench = sub.add_parser("benchmark")
    bench.add_argument("--model")
    bench.add_argument("--runs", type=int, default=3)
    bench.add_argument("--max-tokens", type=int, default=128)
    bench.add_argument("--no-warmup", action="store_true")
    bench.add_argument("--output", default="results/benchmark.json")

    verify = sub.add_parser("verify")
    verify.add_argument("file")

    repair = sub.add_parser("repair")
    repair.add_argument("prompt")
    repair.add_argument("--model")
    repair.add_argument("--max-tokens", type=int, default=512)
    repair.add_argument("--attempts", type=int, default=2)
    repair.add_argument("--output", default="results/generated_solution.py")
    repair.add_argument("--execute", action="store_true")
    repair.add_argument("--timeout", type=int, default=5)
    repair.add_argument("--tests-file")

    args = parser.parse_args()

    if args.backend == "llama.cpp":
        host = args.host or os.getenv(
            "LLAMA_CPP_HOST", "http://127.0.0.1:8080"
        )
        backend = LlamaCppBackend(host)
        default_model = "local-model"
    else:
        host = args.host or os.getenv(
            "OLLAMA_HOST", "http://127.0.0.1:11434"
        )
        backend = OllamaBackend(host)
        default_model = "qwen2.5-coder:1.5b"

    model = getattr(args, "model", None) or default_model
    controller = GenerationController(backend)

    try:
        if args.command == "health":
            data = backend.health()
            result = {
                "ok": True,
                "backend": args.backend,
                "host": host,
                "health": data,
            }
            if args.backend == "ollama":
                result["models"] = [
                    item.get("name") for item in data.get("models", [])
                ]
            print(json.dumps(result, indent=2))

        elif args.command == "generate":
            result = controller.generate(
                GenerationRequest(args.prompt, model, args.max_tokens)
            )
            print(result.response)
            print(
                f"\n[Backend: {args.backend} | "
                f"Throughput: {result.tokens_per_second:.2f} tokens/sec]",
                file=sys.stderr,
            )

        elif args.command == "benchmark":
            results = run_benchmark(
                controller,
                model=model,
                runs=args.runs,
                max_tokens=args.max_tokens,
                warmup=not args.no_warmup,
            )
            results["backend"] = args.backend
            save_results(results, args.output)
            print(json.dumps(results["summary"], indent=2))
            print(f"Saved full results to {args.output}")

        elif args.command == "verify":
            result = check_python_syntax(args.file)
            print(json.dumps(result, indent=2, default=str))
            if not result.get("ok", False):
                return 1

        elif args.command == "repair":
            result = repair_code(
                controller,
                prompt=args.prompt,
                model=model,
                max_tokens=args.max_tokens,
                attempts=args.attempts,
                output_path=args.output,
                execute=args.execute,
                timeout=args.timeout,
                tests_file=args.tests_file,
            )
            print(json.dumps(result, indent=2, default=str))
            if not result.get("success", False):
                return 1

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
