#nLabel jika barang termasuk kategori tidak layak setelah dihitung
NOT_ELIGIBLE_GRADE = "Tidak Layak Disewakan"

def calculate_condition_grade(item):
    """
    Decision Rules:
    - Keamanan <= 2 atau Fungsi == 1 atau Higienitas == 1  -> Tidak Layak Disewakan
    - Fungsi == 2                                          -> Grade D (Cukup)
    - Semua indikator bernilai 4                           -> Grade A (Seperti Baru)
    - Fungsi & Keamanan 4, Fisik & Kelengkapan >= 3        -> Grade B (Sangat Baik)
    - Selebihnya                                           -> Grade C (Baik / Layak Pakai)
    """
    f = item.functional_score
    p = item.physical_score
    s = item.safety_score
    c = item.completeness_score
    h = item.hygiene_score

    if s <= 2 or f == 1 or h == 1:
        return NOT_ELIGIBLE_GRADE
    if f == 2:
        return "Grade D — Cukup"
    if f == 4 and p == 4 and s == 4 and c == 4 and h == 4:
        return "Grade A — Seperti Baru"
    if f >= 4 and s >= 4 and p >= 3 and c >= 3:
        return "Grade B — Sangat Baik"
    return "Grade C — Baik/Layak Pakai"


def is_eligible(item):
    # True kalau barang boleh disewakan
    return calculate_condition_grade(item) != NOT_ELIGIBLE_GRADE