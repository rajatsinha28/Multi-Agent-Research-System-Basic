"""
pipeline.py

Multi-Agent Research Pipeline

Workflow

Planning
    ↓
Searching
    ↓
Reading
    ↓
Writing
    ↓
Summarizing
    ↓
Reviewing
    ↓
(Optional Improvement)
"""

from __future__ import annotations

import time
from typing import Dict, Any

from agents import (
    build_search_agent,
    create_research_plan,
    generate_report,
    review_report,
    create_summary,
    improve_report,
)

from tools import (
    collect_research,
)

# ==========================================================
# PIPELINE
# ==========================================================


def run_research_pipeline(
    topic: str,
    research_length: str = "Medium",
    citation_style: str = "APA",
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Execute the complete multi-agent
    research workflow.
    """

    start_time = time.time()

    state = {

        "topic": topic,

        "plan": "",

        "search_results": "",

        "research": "",

        "report": "",

        "summary": "",

        "feedback": "",

        "sources": [],

        "statistics": {},

    }

    # ======================================================
    # CALLBACK
    # ======================================================

    def update(
        agent: str,
        status: str,
        message: str,
    ):

        print(
            f"[{agent}] "
            f"{status.upper()} "
            f"- {message}"
        )

        if progress_callback:

            progress_callback(
                agent,
                status,
                message,
            )

    try:

        # ==================================================
        # STEP 1
        # ==================================================

        update(
            "Planner Agent",
            "running",
            "Planning research strategy...",
        )

        state["plan"] = create_research_plan(
            topic
        )

        update(
            "Planner Agent",
            "completed",
            "Research plan created.",
        )

        # ==================================================
        # STEP 2
        # ==================================================

        update(
            "Search Agent",
            "running",
            "Searching authoritative sources...",
        )

        search_agent = build_search_agent()

        search_result = search_agent.invoke(

            {

                "messages": [

                    (

                        "user",

                        f"""
Research Topic

{topic}

Research Plan

{state['plan']}

Search for high-quality,
recent and reliable
sources.

Return every useful URL.
""",

                    )

                ]

            }

        )

        state["search_results"] = (
            search_result["messages"][-1].content
        )

        update(

            "Search Agent",

            "completed",

            "Search completed.",

        )

        # ==================================================
        # STEP 3
        # ==================================================

        update(

            "Reader Agent",

            "running",

            "Collecting research sources...",

        )

        collected = collect_research(

            state["search_results"]

        )

        state["sources"] = collected["urls"]

        state["statistics"] = collected["statistics"]

        state["research"] = collected["research"]

        update(

            "Reader Agent",

            "completed",

            f"Collected "
            f"{len(state['sources'])} "
            f"sources.",

        )

        # ==================================================
        # STEP 4
        # WRITER AGENT
        # ==================================================

        update(
            "Writer Agent",
            "running",
            "Generating comprehensive research report...",
        )

        state["report"] = generate_report(

            topic=topic,

            research=state["research"],

            length=research_length,

            citation_style=citation_style,

        )

        update(
            "Writer Agent",
            "completed",
            "Research report generated.",
        )

        # ==================================================
        # STEP 5
        # EXECUTIVE SUMMARY
        # ==================================================

        update(
            "Summary Agent",
            "running",
            "Generating executive summary...",
        )

        state["summary"] = create_summary(
            state["report"]
        )

        update(
            "Summary Agent",
            "completed",
            "Executive summary generated.",
        )

        # ==================================================
        # STEP 6
        # CRITIC AGENT
        # ==================================================

        update(
            "Critic Agent",
            "running",
            "Reviewing research quality...",
        )

        state["feedback"] = review_report(
            state["report"]
        )

        update(
            "Critic Agent",
            "completed",
            "Research review completed.",
        )

        # ==================================================
        # OPTIONAL IMPROVEMENT PASS
        # ==================================================
        #
        # Uncomment this section if you later
        # want the model to automatically revise
        # the report after the critic.
        #
        # update(
        #     "Writer Agent",
        #     "running",
        #     "Improving report..."
        # )
        
        # state["report"] = improve_report(
        #     state["report"],
        #     state["feedback"]
        # )
        
        # update(
        #     "Writer Agent",
        #     "completed",
        #     "Improved report generated."
        # )

        # ==================================================
        # PIPELINE COMPLETE
        # ==================================================

        elapsed_time = round(
            time.time() - start_time,
            2,
        )

        # Update statistics

        state["statistics"].update(

            {

                "research_length": research_length,

                "citation_style": citation_style,

                "execution_time": elapsed_time,

                "report_word_count": len(
                    state["report"].split()
                ),

                "summary_word_count": len(
                    state["summary"].split()
                ),

            }

        )

        update(
            "Pipeline",
            "completed",
            (
                f"Pipeline completed in "
                f"{elapsed_time:.2f} seconds."
            ),
        )

        # ==================================================
        # FINAL RESULT
        # ==================================================

        result = {

            "topic": state["topic"],

            "plan": state["plan"],

            "summary": state["summary"],

            "report": state["report"],

            "feedback": state["feedback"],

            "sources": state["sources"],

            "statistics": state["statistics"],

            "research": state["research"],

            "search_results": state["search_results"],

        }

        return result

    # ======================================================
    # ERROR HANDLING
    # ======================================================

    except Exception as e:

        update(

            "Pipeline",

            "error",

            str(e),

        )

        raise

# ==========================================================
# CLI ENTRY POINT
# ==========================================================

def _validate_length(length: str) -> str:

    allowed = {

        "short": "Short",

        "medium": "Medium",

        "long": "Long",

    }

    return allowed.get(
        length.lower(),
        "Medium",
    )


def _validate_citation(style: str) -> str:

    allowed = {

        "apa": "APA",

        "mla": "MLA",

        "ieee": "IEEE",

        "chicago": "Chicago",

        "harvard": "Harvard",

    }

    return allowed.get(
        style.lower(),
        "APA",
    )


if __name__ == "__main__":

    print("=" * 70)

    print("Multi-Agent Research System")

    print("=" * 70)

    topic = input(
        "\nResearch Topic:\n> "
    ).strip()

    if not topic:

        raise ValueError(
            "Topic cannot be empty."
        )

    length = _validate_length(

        input(
            "\nResearch Length (Short / Medium / Long): "
        ).strip()

        or "Medium"

    )

    citation = _validate_citation(

        input(
            "\nCitation Style (APA / MLA / IEEE / Chicago / Harvard): "
        ).strip()

        or "APA"

    )

    result = run_research_pipeline(

        topic=topic,

        research_length=length,

        citation_style=citation,

    )

    print("\n")

    print("=" * 70)

    print("EXECUTIVE SUMMARY")

    print("=" * 70)

    print(result["summary"])

    print("\n")

    print("=" * 70)

    print("FINAL REPORT")

    print("=" * 70)

    print(result["report"])

    print("\n")

    print("=" * 70)

    print("CRITIC REVIEW")

    print("=" * 70)

    print(result["feedback"])

    print("\n")

    print("=" * 70)

    print("STATISTICS")

    print("=" * 70)

    for key, value in result["statistics"].items():

        print(f"{key:<25}: {value}")

    print("\n")

    print("=" * 70)

    print("SOURCES")

    print("=" * 70)

    for index, url in enumerate(
        result["sources"],
        start=1,
    ):

        print(f"{index}. {url}")

    print("\n")

    print("=" * 70)

    print("Pipeline Finished Successfully")

    print("=" * 70)