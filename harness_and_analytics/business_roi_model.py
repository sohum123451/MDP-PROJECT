"""
Hospital Business ROI & Radiologist Workflow Impact Model.
Member 3 (Manya - Business Systems & CSE DS Lead).
Quantifies the financial, throughput, and operational returns of the EchoScribe platform,
calculating radiologist hours saved, transcription cost reduction, and 3-year ROI.
"""

from typing import Dict, Any


class HospitalBusinessROIModel:
    """
    Financial and operational workflow ROI model for departmental ultrasound integration.
    """

    def __init__(
        self,
        num_ultrasound_machines: int = 4,
        exams_per_day_per_machine: int = 18,
        working_days_per_year: int = 250,
        manual_report_time_minutes: float = 12.0,
        ai_assisted_report_time_minutes: float = 3.5,
        radiologist_hourly_cost_usd: float = 185.0,
        transcription_outsourcing_cost_per_report_usd: float = 2.50,
        on_prem_server_capex_usd: float = 14000.0,
        annual_maintenance_opex_usd: float = 3500.0
    ):
        self.num_machines = num_ultrasound_machines
        self.exams_per_day_per_machine = exams_per_day_per_machine
        self.working_days = working_days_per_year
        self.manual_time_min = manual_report_time_minutes
        self.ai_time_min = ai_assisted_report_time_minutes
        self.rad_hourly_rate = radiologist_hourly_cost_usd
        self.transcription_cost_per_report = transcription_outsourcing_cost_per_report_usd
        self.capex = on_prem_server_capex_usd
        self.annual_opex = annual_maintenance_opex_usd

    def calculate_annual_metrics(self) -> Dict[str, Any]:
        """Calculates operational and financial ROI metrics."""
        total_annual_exams = self.num_machines * self.exams_per_day_per_machine * self.working_days

        # Time Savings
        minutes_saved_per_exam = self.manual_time_min - self.ai_time_min
        total_hours_saved_annually = (total_annual_exams * minutes_saved_per_exam) / 60.0

        # Financial Savings
        radiologist_capacity_value_usd = total_hours_saved_annually * self.rad_hourly_rate
        transcription_outsourcing_savings_usd = total_annual_exams * self.transcription_cost_per_report

        total_annual_gross_benefit_usd = radiologist_capacity_value_usd + transcription_outsourcing_savings_usd
        net_annual_benefit_usd = total_annual_gross_benefit_usd - self.annual_opex

        # Payback period (years)
        payback_period_years = self.capex / net_annual_benefit_usd if net_annual_benefit_usd > 0 else 999.0
        payback_period_months = payback_period_years * 12.0

        # 3-Year Net Present Value (NPV) at 8% discount rate
        discount_rate = 0.08
        npv = -self.capex
        for year in [1, 2, 3]:
            npv += net_annual_benefit_usd / ((1.0 + discount_rate) ** year)

        roi_percentage = (npv / self.capex) * 100.0

        return {
            "total_annual_ultrasound_exams": total_annual_exams,
            "minutes_saved_per_exam": round(minutes_saved_per_exam, 1),
            "radiologist_hours_saved_annually": round(total_hours_saved_annually, 1),
            "radiologist_capacity_value_usd": round(radiologist_capacity_value_usd, 2),
            "transcription_outsourcing_savings_usd": round(transcription_outsourcing_savings_usd, 2),
            "total_annual_gross_benefit_usd": round(total_annual_gross_benefit_usd, 2),
            "net_annual_benefit_usd": round(net_annual_benefit_usd, 2),
            "payback_period_months": round(payback_period_months, 1),
            "three_year_npv_usd": round(npv, 2),
            "three_year_roi_percentage": round(roi_percentage, 1)
        }
