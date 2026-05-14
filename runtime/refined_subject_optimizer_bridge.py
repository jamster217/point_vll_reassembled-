from runtime.refined_subject_vector_loader import get_refined_subject_vector

def build_refined_subject_output(refined_subject: str):
    vector = get_refined_subject_vector(refined_subject)
    if not vector:
        return {
            "status": "missing",
            "refined_subject": refined_subject,
            "vector": None,
            "notes": "No refined subject vector found."
        }

    return {
        "status": "ok",
        "refined_subject": refined_subject,
        "vector": vector,
        "output_packet": {
            "refined_subject": refined_subject,
            "flow": vector.get("flow"),
            "boundary": vector.get("boundary"),
            "memory": vector.get("memory"),
            "novelty": vector.get("novelty"),
            "notes": vector.get("notes"),
        }
    }

if __name__ == "__main__":
    for name in (
        "runtime_systems",
        "compiler_design",
        "self_modeling_systems",
        "machine_consciousness_theory_general",
    ):
        print(build_refined_subject_output(name))

