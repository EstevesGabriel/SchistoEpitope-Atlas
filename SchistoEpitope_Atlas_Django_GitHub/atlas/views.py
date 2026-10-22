from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from .heatmaps import HOST_LABELS, STUDIES, get_host_charts, PROCESSED_ROOT

HOST_ORDER = ["human", "mouse", "rhesus", "baboon", "chimp"]
HOST_SOURCE = {
    "human": "Khouri et al. (2026) — IgG / IgE",
    "mouse": "Farias",
    "baboon": "SchistoEpitope Atlas compilation",
    "chimp": "SchistoEpitope Atlas compilation",
}


def _host_cards():
    cards = []
    for host in HOST_ORDER:
        if host == "rhesus":
            cards.append({
                "key": host,
                "label": HOST_LABELS[host],
                "source": "Vance / Woellner-Santos",
                "url": reverse("atlas:host_explorer", kwargs={"host": host}),
                "available": any((PROCESSED_ROOT / host).glob("*.csv")),
            })
        else:
            cards.append({
                "key": host,
                "label": HOST_LABELS[host],
                "source": HOST_SOURCE.get(host, "Study source documented in the Atlas"),
                "url": reverse("atlas:host_explorer", kwargs={"host": host}),
                "available": any((PROCESSED_ROOT / host).glob("*.csv")),
            })
    return cards


def home(request):
    return render(request, "atlas/home.html", {"host_cards": _host_cards(), "studies": STUDIES})


def host_explorer(request, host):
    if host not in HOST_LABELS:
        raise Http404("Unknown host.")
    if host == "rhesus":
        return render(request, "atlas/rhesus_studies.html", {
            "host_label": HOST_LABELS[host],
            "studies": [
                {**STUDIES["vance-2024"], "url": reverse("atlas:rhesus_explorer", kwargs={"study": "vance-2024"})},
                {**STUDIES["woellner-2024"], "url": reverse("atlas:rhesus_explorer", kwargs={"study": "woellner-2024"})},
            ],
        })
    immunoglobulin = "igg"
    chart_host = host
    measurement_label = "PSA Score"
    source_label = HOST_SOURCE.get(host, "Source study")
    source_description = ""
    if host == "human":
        requested_modality = request.GET.get("immunoglobulin", "igg").strip().lower()
        immunoglobulin = requested_modality if requested_modality in {"igg", "ige"} else "igg"
        if immunoglobulin == "ige":
            chart_host = "human_ige"
            measurement_label = "Fluorescence Intensity"
            source_label = "Khouri et al. (2026) — Human IgE"
            source_description = (
                "Humoral immune profiling of endemic schistosome-exposed individuals reveals "
                "epitopes associated with resistance to reinfection. International Journal of "
                "Infectious Diseases, 171 (2026), 108892. Supplementary Table 4; five categories."
            )
        else:
            source_label = "Khouri et al. (2026) — Human IgG"
            source_description = (
                "Humoral immune profiling of endemic schistosome-exposed individuals reveals "
                "epitopes associated with resistance to reinfection. International Journal of "
                "Infectious Diseases, 171 (2026), 108892."
            )
    charts, errors = get_host_charts(chart_host)
    return render(request, "atlas/explorer.html", {
        "host": host,
        "host_label": HOST_LABELS[host],
        "source_label": source_label,
        "source_description": source_description,
        "charts": charts,
        "errors": errors,
        "immunoglobulin": immunoglobulin,
        "measurement_label": measurement_label,
        "is_human": host == "human",
    })


def rhesus_explorer(request, study):
    if study not in STUDIES:
        raise Http404("Unknown Rhesus study.")
    charts, errors = get_host_charts("rhesus", study)
    return render(request, "atlas/explorer.html", {
        "host": "rhesus",
        "host_label": HOST_LABELS["rhesus"],
        "source_label": STUDIES[study]["label"],
        "study_description": STUDIES[study]["description"],
        "charts": charts,
        "errors": errors,
        "is_rhesus_study": True,
        "study_key": study,
        "measurement_label": "PSA Score",
    })
