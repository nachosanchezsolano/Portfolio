"""Evaluate ranked retrieval results offline; remote queries require --remote.

Results format: {"question-id": ["projects/source.md", ...]}.
Follow-up cases include history/page_context for the query resolver separately.
Offline results measure retrieval only, not generation faithfulness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def evaluate(questions: list[dict], results: dict[str, list[str]], k: int = 4) -> dict:
    if k < 1:
        raise ValueError('k must be positive')
    recalls, reciprocals, failures, abstentions = [], [], [], []
    for item in questions:
        ranked = list(dict.fromkeys(results.get(item['id'], [])))[:k]
        relevant = set(item['relevant_sources'])
        if not relevant:
            abstentions.append(not ranked)
            if ranked:
                failures.append(item['id'])
            continue
        recall = len(relevant.intersection(ranked)) / len(relevant)
        rank = next((i for i, source in enumerate(ranked, 1) if source in relevant), None)
        recalls.append(recall)
        reciprocals.append(1 / rank if rank else 0)
        if not rank:
            failures.append(item['id'])
    return {'k': k, 'questions': len(questions), 'recall_at_k': sum(recalls) / len(recalls) if recalls else None,
            'mrr': sum(reciprocals) / len(reciprocals) if reciprocals else None,
            'abstention_accuracy': sum(abstentions) / len(abstentions) if abstentions else None,
            'failed_ids': failures}


def remote_results(questions: list[dict], index: str, min_score: float, k: int) -> dict:
    # Explicit remote mode incurs Workers AI calls; no default network activity.
    from upsert_vectorize import EMBEDDING_MODEL, api_json, cloudflare_credentials, with_cloudflare_fallback
    credentials = cloudflare_credentials()
    if not credentials:
        raise SystemExit('Cloudflare credentials are required for --remote')
    results = {}
    for item in questions:
        query = item.get('retrieval_query', item['question'])
        def retrieve(credential):
            base = f'https://api.cloudflare.com/client/v4/accounts/{credential.account_id}'
            vector = api_json(f'{base}/ai/run/{EMBEDDING_MODEL}', credential.token, {'text': [query]})['data'][0]
            return api_json(f'{base}/vectorize/v2/indexes/{index}/query', credential.token, {'vector': vector, 'topK': k, 'returnMetadata': 'all'})
        matches = with_cloudflare_fallback(credentials, retrieve).get('matches', [])
        results[item['id']] = [match['metadata']['source'] for match in matches if match.get('score', 0) >= min_score and match.get('metadata', {}).get('source')]
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--questions', type=Path, default=ROOT / 'evaluation/questions.json')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--results', type=Path)
    source.add_argument('--remote', action='store_true')
    parser.add_argument('--index', default='portfolio-knowledge')
    parser.add_argument('--min-score', type=float, default=0.7)
    parser.add_argument('--k', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.k <= 20 or not 0 <= args.min_score <= 1:
        parser.error('k must be 1..20 and min-score 0..1')
    questions = json.loads(args.questions.read_text(encoding='utf-8'))
    results = remote_results(questions, args.index, args.min_score, args.k) if args.remote else json.loads(args.results.read_text(encoding='utf-8'))
    print(json.dumps(evaluate(questions, results, args.k), indent=2))


if __name__ == '__main__':
    main()
