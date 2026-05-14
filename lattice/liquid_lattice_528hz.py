LATTICE Liquid528

FLOW INIT
    MEM nodes
    MEM resonance_field
END

BOUND INJECT
    TAKE tone
    SHIFT resonance_field WITH tone*0.528
END

FLOW PROJECT
    TAKE emotion
    MERGE out = emotion * resonance_field
    RETURN out
END

