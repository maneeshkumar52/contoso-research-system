import asyncio, sys
sys.path.insert(0, '.')

async def main():
    print("=== Contoso Research System - End-to-End Demo ===\n")

    # Test 1: Shared models
    from shared.models import SpecialistType, ResearchRequest, SpecialistOutput
    req = ResearchRequest(
        topic="Azure AI Market Analysis",
        company_name="Microsoft",
        date_range="2024-Q4",
        requested_by="analyst@contoso.com",
        run_id="demo-001"
    )
    print(f"ResearchRequest: {req.topic} for {req.company_name}")

    # Test 2: Compliance rules (no Azure needed)
    from compliance_gate.rules import FCA_RULES
    print(f"\nFCA Rules loaded: {len(FCA_RULES)} rules")
    for rule in FCA_RULES[:3]:
        print(f"  - {rule.rule_id}: {rule.description[:60]}...")

    # Test 3: Local service bus
    from shared.service_bus import ServiceBusHelper
    sb = ServiceBusHelper(connection_string="placeholder", local_mode=True)
    await sb.publish("test-queue", {"message": "hello", "type": "test"})
    print(f"\nServiceBus (LOCAL_MODE): message published to queue")

    # Test 4: Specialist output model
    output = SpecialistOutput(
        specialist_type=SpecialistType.FINANCIAL_ANALYST,
        analysis_text="Microsoft shows strong cloud revenue growth of 23% YoY with expanding margins.",
        confidence_score=0.87,
        key_findings=["23% cloud revenue growth", "Operating margin expansion to 43%", "AI services driving new revenue streams"],
        data_sources=["Q4 2024 earnings report", "Bloomberg data"],
        processing_time_seconds=12.3
    )
    print(f"\nSpecialistOutput: {output.specialist_type.value}")
    print(f"  Confidence: {output.confidence_score}")
    print(f"  Findings: {output.key_findings}")

    print("\n=== Core pipeline architecture validated ===")

asyncio.run(main())
