import urllib.request

GUTENBERG_URL = (
    "https://www.gutenberg.org/files/64317/64317-0.txt"
)

def calculate_ground_truth(url: str):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        text = resp.read().decode(
            "utf-8",
            errors="replace"
        )

    lines = text.splitlines()

    return {
        "total_lines": len(lines),
        "gatsby_matching_lines": sum(
            "Gatsby" in line for line in lines
        ),
        "gatsby_occurrences": sum(
            line.count("Gatsby") for line in lines
        ),
        "first_daisy_line": next(
            (
                i for i, line in enumerate(lines, 1)
                if "Daisy" in line
            ),
            None
        ),
        "daisy_matching_lines": sum(
            "Daisy" in line for line in lines
        ),
        "daisy_occurrences": sum(
            line.count("Daisy") for line in lines
        ),
    }


ground_truth = calculate_ground_truth(GUTENBERG_URL)

print("GROUND TRUTH:")
for key, value in ground_truth.items():
    print(f"{key}: {value}")

# ```
# GROUND TRUTH:
# total_lines: 6407
# gatsby_matching_lines: 258
# gatsby_occurrences: 264
# first_daisy_line: 181
# daisy_matching_lines: 184
# daisy_occurrences: 186
# ```