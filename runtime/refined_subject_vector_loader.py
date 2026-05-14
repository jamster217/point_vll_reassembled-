from spiral_language.refined_subject_vector_seeds import REFINED_SUBJECT_VECTOR_SEEDS

def get_refined_subject_vector(name: str):
    return REFINED_SUBJECT_VECTOR_SEEDS.get(name)

if __name__ == "__main__":
    for key in ("runtime_systems", "compiler_design", "language_design"):
        print(key, "->", get_refined_subject_vector(key))

