# Static structural representation of the 528 lattice kernel
LATTICE_KERNEL_528 = {
    "name": "Liquid528",
    "flows": {
        "INIT": {
            "MEM": {
                "nodes": None,
                "resonance_field": 1.0
            }
        },
        "INJECT": {
            "TAKE": ["tone"],
            "SHIFT": {
                "target": "resonance_field",
                "expression": "tone * 0.528"
            }
        },
        "PROJECT": {
            "TAKE": ["emotion"],
            "MERGE": {
                "out": "emotion * resonance_field"
            },
            "RETURN": "out"
        }
    },
    "status": "static",
    "version": "1.0"
}

