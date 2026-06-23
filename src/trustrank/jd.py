from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class JobSpec:
    title: str = "Senior AI Engineer - Founding Team (Redrob AI)"

    yoe_ideal_low: float = 6.0
    yoe_ideal_high: float = 8.0
    yoe_ok_low: float = 5.0
    yoe_ok_high: float = 9.0

    base_scores: dict = field(default_factory=lambda: {
        "A_ranking_recsys": 94.0,   
        "B_applied_ml": 76.0,       
        "C_light_ml": 50.0,         
        "D_data_eng": 34.0,         
        "D_generic_swe": 28.0,      
        "E_non_tech": 6.0,          
    })

    cv_speech_penalty: float = 0.45     
    services_penalty: float = 0.60
    decoy_summary_penalty: float = 0.35

    availability_min: float = 0.60
    availability_max: float = 1.05


REDROB_SENIOR_AI_ENGINEER = JobSpec()
