from runtime.refined_subject_optimizer_bridge import build_refined_subject_output
import json
import sys

def run_build_optimizer_seed(refined_subject: str):
    return build_refined_subject_output(refined_subject)

def main():
    refined_subject = sys.argv[1] if len(sys.argv) > 1 else "compiler_design"
    out = run_build_optimizer_seed(refined_subject)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

