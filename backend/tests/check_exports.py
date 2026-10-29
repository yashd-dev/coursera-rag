import sys, tempfile, shutil, json
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import latexbuild

for template in ("ieee", "springer"):
    root = Path("/tmp/export-fixture") / template
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    shutil.copytree(latexbuild.TEMPLATE_DIR / template, root / "paper")
    tex = root / "paper/main.tex"
    s = (
        tex.read_text()
        .replace("PAPER TITLE", "Export Fixture: Not a Research Result")
        .replace(
            "ABSTRACT",
            "This synthetic fixture checks export structure only. No literature review or research was performed.",
        )
        .replace(
            "TEXT",
            r"Fixture citation~\cite{fixture2026}.\section{Equation and Table}The identity $a+b=b+a$ is a formatting example.\begin{equation}a+b=b+a\end{equation}\begin{tabular}{ll}Field & Value\\Fixture & Synthetic\end{tabular}",
        )
    )
    tex.write_text(s)
    (root / "paper/refs.bib").write_text(
        "@article{fixture2026,author={Fixture Author},title={Synthetic export fixture},journal={Fixture Journal},year={2026}}"
    )
    with patch.object(latexbuild.db, "thread_dir", return_value=root):
        result = latexbuild.build("fixture")
        word = latexbuild.export_docx("fixture", template)
        check = latexbuild.verify_docx("fixture") if word["ok"] else {}
        print(
            template,
            json.dumps(
                {
                    "build": result,
                    "docx_ok": word["ok"],
                    "wordlog": word["log"],
                    "docx_check": check,
                },
                default=str,
            ),
        )
        for name, p in [
            ("pdf", root / "paper/main.pdf"),
            ("docx", root / "paper/paper.docx"),
            ("word-render", root / "paper/docx-check/paper.pdf"),
        ]:
            if p.exists():
                shutil.copy(
                    p,
                    str(
                        root
                        / f'{template}-fixture.{"docx" if name=="docx" else name+".pdf"}'
                    ),
                )
