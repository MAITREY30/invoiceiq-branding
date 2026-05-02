from .invoice_utils import get_directory_structure, get_invoice_count_in_subdirs

def refresh_invoice_counts():
    dirs = get_directory_structure()
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    counts = {
        "auto_processed": get_invoice_count_in_subdirs(dirs["auto_processed"]),
        "pending_review": get_invoice_count_in_subdirs(dirs["pending_review"]),
        "approved": get_invoice_count_in_subdirs(dirs["approved"]),
        "rejected": get_invoice_count_in_subdirs(dirs["rejected"]),
    }

    total = sum(counts.values())
    counts["total_received"] = total
    counts["successfully_processed"] = counts["auto_processed"] + counts["approved"]

    if total > 0:
        counts["acceptance_rate"] = (counts["successfully_processed"] / total) * 100
        counts["auto_processing_rate"] = (counts["auto_processed"] / total) * 100
        counts["review_efficiency"] = max(0.0, 100.0 - (counts["pending_review"] / total) * 100)
        counts["risk_score"] = min(
            100.0,
            max(
                0.0,
                (counts["pending_review"] * 0.6)
                + (counts["rejected"] * 1.2)
                + ((100.0 - counts["acceptance_rate"]) * 0.4)
            )
        )
        counts["health_score"] = max(0.0, 100.0 - counts["risk_score"])
    else:
        counts["acceptance_rate"] = 0
        counts["auto_processing_rate"] = 0
        counts["review_efficiency"] = 0
        counts["risk_score"] = 0
        counts["health_score"] = 100

    return counts
