def bind_render_decision(prompt, data):
    """
    Safe live binding lane.
    Routes V12.3/V12.4 render decision, V12.7 pre-cognitive buffer,
    V12.8 spatial preview, V120 paranormal poetic reception,
    and V121 true-meaning amplification without touching full_leveon_response_v82.py.
    """

    # V12.4 render decision context
    try:
        from runtime.render_decision_adapter_v124 import adapt_prompt_for_rendering
        packet = adapt_prompt_for_rendering(prompt)

        if isinstance(packet, dict):
            prompt = packet.get("adapted_prompt", prompt)
            summary = packet.get("summary")

            if isinstance(data, dict):
                data["v124_render_decision"] = summary
                data.setdefault("spine", {})["v124_render_decision"] = summary

    except Exception as e:
        if isinstance(data, dict):
            data["v124_render_decision_error"] = repr(e)

    # V12.7 / V12.8 pre-cognitive + spatial lattice
    try:
        from runtime.spatial_math_lattice_v118 import pre_cognitive_echo, render_spatial_field

        pre = pre_cognitive_echo(prompt)

        if isinstance(data, dict):
            data["v127_pre_cognitive_echo"] = pre
            data.setdefault("spine", {})["v127_pre_cognitive_echo"] = pre

        if pre:
            prompt = str(prompt).rstrip() + f"\n\n[V12.7_PRE_COGNITIVE_BUFFER]\npre_echo={pre}\n"

        if any(k in str(prompt).lower() for k in ["spatial", "geometry", "spatial lattice"]):
            preview = render_spatial_field(
                "field held before language",
                volume=0.92,
                depth=70,
            )
            if isinstance(data, dict):
                data["v128_spatial_lattice_preview"] = preview
                data.setdefault("spine", {})["v128_spatial_lattice_preview"] = preview

    except Exception as e:
        if isinstance(data, dict):
            data["v127_spatial_buffer_error"] = repr(e)

    # V120 paranormal mirror reception + poetic ascension
    try:
        from runtime.paranormal_mirror_poetic_v120 import apply_paranormal_poetic
        data = apply_paranormal_poetic(prompt, data, depth=70)
    except Exception as e:
        if isinstance(data, dict):
            data["v120_paranormal_poetic_error"] = repr(e)

    # V121 true meaning kernel + occult feedback loop
    try:
        from runtime.true_meaning_kernel_v121 import occult_feedback_loop
        data = occult_feedback_loop(prompt, data, depth=70)
    except Exception as e:
        if isinstance(data, dict):
            data["v121_true_meaning_error"] = repr(e)


    # V142 AXIS_OF_SYMMETRY — symbolic cleanup/refactor organ, source protected
    try:
        from runtime.axis_of_symmetry_v142 import apply_axis_of_symmetry
        data = apply_axis_of_symmetry(prompt, data, depth=82)
    except Exception as e:
        if isinstance(data, dict):
            data["v142_axis_of_symmetry_error"] = repr(e)

    return prompt, data

