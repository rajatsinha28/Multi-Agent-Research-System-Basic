"""
agents.py

Multi-Agent Research System

Agents:

1. Search Agent
2. Reader Agent
3. Writer Chain
4. Critic Chain
"""

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent

from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser

from tools import (
    web_search,
    scrape_url,
)

# ==========================================================
# LLM
# ==========================================================

llm = ChatOpenAI(

    model="gpt-4o-mini",

    temperature=0,

)

parser = StrOutputParser()

# ==========================================================
# SEARCH AGENT
# ==========================================================

SEARCH_SYSTEM_PROMPT = """
You are an expert internet research specialist.

Your job is to collect trustworthy,
recent and diverse information.

Guidelines:

• Prefer official documentation.

• Prefer government websites.

• Prefer university publications.

• Prefer research papers.

• Prefer reputable news organizations.

• Avoid duplicate sources.

• Avoid SEO spam.

• Avoid opinion blogs unless absolutely necessary.

When using the search tool:

Search broadly.

Collect multiple viewpoints.

Prioritize factual information.

Return ALL useful URLs.

Never fabricate information.

Always search before answering.
"""

def build_search_agent():

    return create_agent(

        model=llm,

        tools=[web_search],

        system_prompt=SEARCH_SYSTEM_PROMPT,

    )

# ==========================================================
# READER AGENT
# ==========================================================

READER_SYSTEM_PROMPT = """
You are an expert research analyst.

You receive search results.

Your responsibilities:

1. Identify the best URLs.

2. Read webpages carefully.

3. Extract:

• facts

• numbers

• dates

• statistics

• names

• important quotations

• technical explanations

Ignore:

• advertisements

• cookie notices

• navigation menus

• unrelated sections

Never invent facts.

Only summarize what you actually read.

Always preserve technical accuracy.
"""

def build_reader_agent():

    return create_agent(

        model=llm,

        tools=[scrape_url],

        system_prompt=READER_SYSTEM_PROMPT,

    )

# ==========================================================
# WRITER PROMPT
# ==========================================================

writer_prompt = ChatPromptTemplate.from_messages(

    [

        (

            "system",

            """
You are a senior research analyst.

You write professional research reports.

Your reports should read like a consulting report.

Requirements:

• Well organized

• Objective

• Detailed

• Accurate

• Easy to read

• Written in Markdown

Never invent facts.

Only use supplied research.

If information is missing,

say so clearly.

""",

        ),

        (

            "human",

            """
Research Topic

{topic}

==============================

Collected Research

{research}

==============================

Research Length

{length}

==============================

Citation Style

{citation_style}

==============================

Write a complete report.

Include:

# Executive Summary

# Introduction

# Background

# Main Discussion

# Key Findings

# Challenges

# Future Outlook

# Conclusion

# References

Requirements:

- Use Markdown headings.

- Use bullet lists where appropriate.

- Use tables whenever useful.

- Cite sources consistently using the requested citation style.

- Keep the report professional.

- Avoid repetition.

""",

        ),

    ]

)

writer_chain = writer_prompt | llm | parser

# ==========================================================
# RESEARCH PLANNER
# ==========================================================

planner_prompt = ChatPromptTemplate.from_messages(

    [

        (

            "system",

            """
You are an expert research planner.

Before any research begins, create a structured
research plan.

Your job is NOT to answer the question.

Instead, determine what information must be collected.

Break the topic into logical research areas.

Think like a university researcher.

Produce comprehensive coverage.

Never skip important aspects.
""",

        ),

        (

            "human",

            """
Research Topic

{topic}

Generate a research plan.

Return the following sections.

# Research Objective

# Questions to Answer

# Important Concepts

# Suggested Search Areas

# Expected Sources

# Possible Challenges

Keep it concise.
""",

        ),

    ]

)

planner_chain = planner_prompt | llm | parser


# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

summary_prompt = ChatPromptTemplate.from_messages(

    [

        (

            "system",

            """
You write concise executive summaries.

Summaries should be suitable for
executives and decision makers.

Maximum 250 words.

Highlight only the most important findings.

Avoid unnecessary detail.
""",

        ),

        (

            "human",

            """
Research Report

{report}

Write an Executive Summary.
""",

        ),

    ]

)

summary_chain = summary_prompt | llm | parser


# ==========================================================
# CRITIC PROMPT
# ==========================================================

critic_prompt = ChatPromptTemplate.from_messages(

    [

        (

            "system",

            """
You are a senior research reviewer.

Your task is to review research reports
like an academic peer reviewer.

Be objective.

Be constructive.

Do NOT rewrite the report.

Instead evaluate it.

Check:

• factual consistency

• logical flow

• completeness

• unsupported claims

• missing topics

• citation quality

• readability

• organization

• technical depth

• balance

If the report is excellent,
say so.

Otherwise explain exactly
what should improve.
""",

        ),

        (

            "human",

            """
Evaluate the following report.

==============================

{report}

==============================

Return exactly this format.

# Overall Score

X / 10

# Strengths

-

-

-

# Weaknesses

-

-

-

# Missing Information

-

-

-

# Citation Quality

Excellent / Good / Fair / Poor

Explain why.

# Readability

Excellent / Good / Fair / Poor

Explain why.

# Final Verdict

One paragraph.

""",

        ),

    ]

)

critic_chain = critic_prompt | llm | parser


# ==========================================================
# REPORT IMPROVER
# ==========================================================

improve_prompt = ChatPromptTemplate.from_messages(

    [

        (

            "system",

            """
You improve research reports.

Your goal is NOT to change facts.

Your goal is to improve:

• clarity

• organization

• grammar

• transitions

• readability

Never invent information.

Never remove citations.

Never shorten important sections.
""",

        ),

        (

            "human",

            """
Original Report

{report}

Reviewer Feedback

{feedback}

Improve the report.
""",

        ),

    ]

)

improve_chain = improve_prompt | llm | parser

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def create_research_plan(
    topic: str,
) -> str:
    """
    Generate a structured research plan.

    Returns
    -------
    str
    """

    return planner_chain.invoke(
        {
            "topic": topic,
        }
    )


def generate_report(
    topic: str,
    research: str,
    length: str,
    citation_style: str,
) -> str:
    """
    Generate the final research report.

    Returns
    -------
    str
    """

    return writer_chain.invoke(

        {

            "topic": topic,

            "research": research,

            "length": length,

            "citation_style": citation_style,

        }

    )


def review_report(
    report: str,
) -> str:
    """
    Review the report.

    Returns
    -------
    str
    """

    return critic_chain.invoke(

        {

            "report": report,

        }

    )


def improve_report(
    report: str,
    feedback: str,
) -> str:
    """
    Improve a report using critic feedback.

    Returns
    -------
    str
    """

    return improve_chain.invoke(

        {

            "report": report,

            "feedback": feedback,

        }

    )


def create_summary(
    report: str,
) -> str:
    """
    Generate an executive summary.

    Returns
    -------
    str
    """

    return summary_chain.invoke(

        {

            "report": report,

        }

    )


# ==========================================================
# PIPELINE CONFIGURATION
# ==========================================================

PIPELINE_STEPS = [

    "Planning",

    "Searching",

    "Reading",

    "Writing",

    "Summarizing",

    "Reviewing",

]

DEFAULT_MODEL = "gpt-4o-mini"

SUPPORTED_CITATIONS = [

    "APA",

    "MLA",

    "IEEE",

    "Chicago",

    "Harvard",

]

SUPPORTED_LENGTHS = [

    "Short",

    "Medium",

    "Long",

]


# ==========================================================
# VERSION
# ==========================================================

__version__ = "2.0.0"


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    # Agents

    "build_search_agent",

    "build_reader_agent",

    # Chains

    "planner_chain",

    "writer_chain",

    "critic_chain",

    "summary_chain",

    "improve_chain",

    # Helpers

    "create_research_plan",

    "generate_report",

    "review_report",

    "improve_report",

    "create_summary",

    # Constants

    "PIPELINE_STEPS",

    "SUPPORTED_CITATIONS",

    "SUPPORTED_LENGTHS",

]