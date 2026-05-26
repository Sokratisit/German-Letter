(() => {
    const form = document.getElementById("letter-form");
    if (!form) {
        return;
    }

    const field = (id) => document.getElementById(id);

    const dateField = field("date_iso");
    const filenameDateHint = field("filename_date_hint");
    const filenamePreviewField = field("filename_preview");
    const filenameAddresseeField = field("filename_addressee");
    const signatureField = field("signature");
    const bodyModeMarkdownField = field("body_mode_markdown");
    const bodyModeLatexField = field("body_mode_latex");
    const bodyModeHelp = field("body-mode-help");

    const senderTitleField = field("sender_title");
    const senderFirstNameField = field("sender_first_name");
    const senderLastNameField = field("sender_last_name");
    const recipientLastNameField = field("recipient_last_name");
    const streetFieldPairs = [
        [field("sender_street"), field("sender_street_number")],
        [field("recipient_street"), field("recipient_street_number")],
    ];

    const setAutofillMode = (element, isUserEdited) => {
        if (!element) {
            return;
        }
        element.dataset.userEdited = isUserEdited ? "true" : "false";
    };

    const parseDateToIso = (rawValue) => {
        const value = rawValue.trim();
        if (!value) {
            return "";
        }

        const isoMatch = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (isoMatch) {
            const parsed = new Date(`${isoMatch[1]}-${isoMatch[2]}-${isoMatch[3]}T00:00:00`);
            if (!Number.isNaN(parsed.getTime())) {
                return `${isoMatch[1]}-${isoMatch[2]}-${isoMatch[3]}`;
            }
            return "";
        }

        const localMatch = value.match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
        if (!localMatch) {
            return "";
        }
        const day = Number(localMatch[1]);
        const month = Number(localMatch[2]);
        const year = Number(localMatch[3]);
        const parsed = new Date(year, month - 1, day);
        if (
            Number.isNaN(parsed.getTime())
            || parsed.getFullYear() !== year
            || parsed.getMonth() !== month - 1
            || parsed.getDate() !== day
        ) {
            return "";
        }
        const mm = String(month).padStart(2, "0");
        const dd = String(day).padStart(2, "0");
        return `${year}-${mm}-${dd}`;
    };

    const syncFilenamePreview = () => {
        if (!filenamePreviewField || !filenameAddresseeField || !filenameDateHint) {
            return;
        }
        const datePart = filenameDateHint.value.trim() || "YYYY-MM-DD";
        const addresseePart = filenameAddresseeField.value.trim() || "Empfänger";
        filenamePreviewField.textContent = `${datePart} ${addresseePart}.pdf`;
    };

    const MARKDOWN_HELP_HTML = [
        "<p><strong>Kursiv</strong> <code>*Text*</code></p>",
        "<p><strong>Fett</strong> <code>**Text**</code></p>",
        "<p><strong>Umbruch</strong> Zeile mit zwei Leerzeichen beenden</p>",
        "<p><strong>Absatz</strong> Leerzeile</p>",
        "<p><strong>Liste (unsortiert)</strong> <code>- Punkt</code></p>",
        "<p><strong>Liste (sortiert)</strong> <code>1. Punkt</code></p>",
    ].join("");

    const LATEX_HELP_HTML = [
        "<p><strong>Kursiv</strong> <code>\\textit{Text}</code></p>",
        "<p><strong>Fett</strong> <code>\\textbf{Text}</code></p>",
        "<p><strong>Umbruch</strong> <code>\\\\</code> am Zeilenende</p>",
        "<p><strong>Absatz</strong> Leerzeile</p>",
        "<p><strong>Liste (unsortiert)</strong></p>",
        "<pre><code>\\begin{itemize}\n  \\item Punkt eins\n  \\item Punkt zwei\n\\end{itemize}</code></pre>",
        "<p><strong>Liste (sortiert)</strong></p>",
        "<pre><code>\\begin{enumerate}\n  \\item Punkt eins\n  \\item Punkt zwei\n\\end{enumerate}</code></pre>",
    ].join("");

    const syncBodyModeHelp = () => {
        if (!bodyModeHelp) {
            return;
        }
        bodyModeHelp.innerHTML = bodyModeLatexField && bodyModeLatexField.checked
            ? LATEX_HELP_HTML
            : MARKDOWN_HELP_HTML;
    };

    const syncFilenameSuggestion = () => {
        if (!recipientLastNameField || !filenameAddresseeField) {
            return;
        }
        if (filenameAddresseeField.dataset.userEdited === "true") {
            return;
        }
        filenameAddresseeField.value = recipientLastNameField.value.trim();
        syncFilenamePreview();
    };

    const syncSignatureSuggestion = () => {
        if (!senderTitleField || !senderFirstNameField || !senderLastNameField || !signatureField) {
            return;
        }
        if (signatureField.dataset.userEdited === "true") {
            return;
        }
        const parts = [
            senderTitleField.value.trim(),
            senderFirstNameField.value.trim(),
            senderLastNameField.value.trim(),
        ].filter(Boolean);
        signatureField.value = parts.join(" ");
    };

    if (filenameAddresseeField) {
        syncFilenameSuggestion();
        if (recipientLastNameField) {
            recipientLastNameField.addEventListener("input", syncFilenameSuggestion);
        }
        filenameAddresseeField.addEventListener("input", () => {
            setAutofillMode(filenameAddresseeField, Boolean(filenameAddresseeField.value.trim()));
            syncFilenamePreview();
        });
    }

    if (signatureField) {
        syncSignatureSuggestion();
        [senderTitleField, senderFirstNameField, senderLastNameField].forEach((element) => {
            if (element) {
                element.addEventListener("input", syncSignatureSuggestion);
            }
        });
        signatureField.addEventListener("input", () => {
            setAutofillMode(signatureField, Boolean(signatureField.value.trim()));
        });
    }

    if (dateField && filenameDateHint) {
        const syncDateHint = () => {
            filenameDateHint.value = parseDateToIso(dateField.value);
            syncFilenamePreview();
        };
        syncDateHint();
        dateField.addEventListener("input", syncDateHint);
    }

    syncFilenamePreview();
    syncBodyModeHelp();

    [bodyModeMarkdownField, bodyModeLatexField].forEach((element) => {
        if (element) {
            element.addEventListener("change", syncBodyModeHelp);
        }
    });

    const moveTrailingHouseNumber = (streetField, numberField) => {
        if (!streetField || !numberField) {
            return;
        }
        const match = streetField.value.match(/^(.*\S)\s+(\d+)$/);
        if (!match) {
            return;
        }
        streetField.value = match[1];
        numberField.value = match[2];
        numberField.focus();
        const end = numberField.value.length;
        numberField.setSelectionRange(end, end);
    };

    streetFieldPairs.forEach(([streetField, numberField]) => {
        if (!streetField || !numberField) {
            return;
        }
        streetField.addEventListener("change", () => moveTrailingHouseNumber(streetField, numberField));
        streetField.addEventListener("blur", () => moveTrailingHouseNumber(streetField, numberField));
    });

    form.addEventListener("submit", (event) => {
        let isValid = true;

        if (dateField && dateField.value && !parseDateToIso(dateField.value)) {
            dateField.setCustomValidity("Datum muss im Format TT.MM.JJJJ sein.");
            isValid = false;
        } else if (dateField) {
            dateField.setCustomValidity("");
        }

        if (!isValid) {
            event.preventDefault();
            form.reportValidity();
            return;
        }

        event.preventDefault();
        submitFormAsDownload();
    });

    const submitFormAsDownload = async () => {
        const formData = new FormData(form);
        const actionUrl = form.getAttribute("action") || "/generate";

        try {
            const response = await fetch(actionUrl, {
                method: "POST",
                body: formData,
                credentials: "same-origin",
            });

            const contentType = response.headers.get("content-type") || "";
            if (response.ok && contentType.includes("application/pdf")) {
                const blob = await response.blob();
                const objectUrl = URL.createObjectURL(blob);
                const contentDisposition = response.headers.get("content-disposition") || "";
                const filenameMatch = contentDisposition.match(/filename\*?=(?:UTF-8''|")?([^";\r\n]+)/i);
                const filename = filenameMatch ? decodeURIComponent(filenameMatch[1].replace(/"/g, "")) : "letter.pdf";

                const link = document.createElement("a");
                link.href = objectUrl;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                link.remove();
                URL.revokeObjectURL(objectUrl);
                return;
            }

            const html = await response.text();
            document.open();
            document.write(html);
            document.close();
        } catch (_err) {
            form.submit();
        }
    };
})();
