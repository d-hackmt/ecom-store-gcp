"""
Online (live) evaluation for the shopping agent.

Unlike backend/evals/chatbot_evals.py — a batch suite you run by hand — these
evaluators are attached to the live `agent` (see agent.py) via the
`OnlineEvaluation` capability. They fire in the background after every real
agent run, stream pass/fail + numeric scores to Logfire, and never block or
slow down the user's request.

Seen in Logfire under: AI Evaluations → Live monitoring (target: "chatbot").

Requires LOGFIRE_TOKEN in the environment for scores to actually leave the
process; otherwise everything here is a cheap no-op.
"""
from dataclasses import dataclass

from pydantic_evals.evaluators import Evaluator, EvaluatorContext, LLMJudge
from pydantic_evals.online import OnlineEvalConfig, OnlineEvaluator
from pydantic_evals.online_capability import OnlineEvaluation


@dataclass
class ReplyNotEmpty(Evaluator):
    """The agent produced a non-empty text reply (catches silent/blank failures)."""

    def evaluate(self, ctx: EvaluatorContext) -> bool:
        return bool(str(ctx.output or "").strip())


@dataclass
class ReplyLength(Evaluator):
    """Raw character count of the reply — a numeric score to trend over time."""

    def evaluate(self, ctx: EvaluatorContext) -> float:
        return float(len(str(ctx.output or "")))


# LLM-graded quality check. Same judge model as the offline suite. Sampled at
# 30% so the background judge calls don't eat into Groq's 8000 TPM limit that
# the live chat traffic is already sharing.
_quality_judge = OnlineEvaluator(
    evaluator=LLMJudge(
        rubric=(
            "The reply is from ClothStore's shopping assistant. It is on-topic "
            "(clothing/shopping, or a natural greeting/identity answer, or a "
            "polite refusal pointing to customer care), never rude, and never "
            "invents specific product names, prices, or stock details."
        ),
        model="groq:openai/gpt-oss-120b",
    ),
    sample_rate=0.3,
)


online_evaluation = OnlineEvaluation(
    evaluators=[
        ReplyNotEmpty(),
        ReplyLength(),
        _quality_judge,
    ],
    # default_sample_rate applies to the bare (non-LLM) evaluators above.
    config=OnlineEvalConfig(default_sample_rate=1.0),
)
