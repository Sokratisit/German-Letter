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

    const senderTitleField = field("sender_title");
    const senderFirstNameField = field("sender_first_name");
    const senderLastNameField = field("sender_last_name");
    const recipientLastNameField = field("recipient_last_name");

    const setAutofillMode = (element, isUserEdited) => {
        if (!element) {
            return;
        }
        element.dataset.userEdited = isUserEdited ? "true" : "false";
    };

    const syncFilenamePreview = () => {
        if (!filenamePreviewField || !filenameAddresseeField || !filenameDateHint) {
            return;
        }
        const datePart = filenameDateHint.value.trim() || "YYYY-MM-DD";
        const addresseePart = filenameAddresseeField.value.trim() || "Empfänger";
        filenamePreviewField.value = `${datePart} ${addresseePart}.pdf`;
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
            filenameDateHint.value = dateField.value;
            syncFilenamePreview();
        };
        syncDateHint();
        dateField.addEventListener("input", syncDateHint);
    }

    syncFilenamePreview();

    form.addEventListener("submit", (event) => {
        let isValid = true;

        if (dateField && dateField.value && !/^\d{4}-\d{2}-\d{2}$/.test(dateField.value)) {
            dateField.setCustomValidity("Datum muss im Format YYYY-MM-DD sein.");
            isValid = false;
        } else if (dateField) {
            dateField.setCustomValidity("");
        }

        if (!isValid) {
            event.preventDefault();
            form.reportValidity();
        }
    });
})();
