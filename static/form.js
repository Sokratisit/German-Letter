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

    const fillAlbertMarksButton = field("fill-albert-marks");
    const fillSampleLetterButton = field("fill-sample-letter");

    const setFieldValue = (id, value) => {
        const element = field(id);
        if (!element) {
            return;
        }
        element.value = value;
        element.dispatchEvent(new Event("input", { bubbles: true }));
    };

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

    const fillAlbertMarks = () => {
        setAutofillMode(signatureField, false);
        setFieldValue("sender_title", "");
        setFieldValue("sender_first_name", "Albert");
        setFieldValue("sender_last_name", "Marks");
        setFieldValue("sender_extra", "");
        setFieldValue("sender_street", "Stammheimer Str.");
        setFieldValue("sender_street_number", "94");
        setFieldValue("sender_postal_code", "50735");
        setFieldValue("sender_city", "Köln");
        setFieldValue("sender_phone", "");
        setFieldValue("sender_mobile_phone", "");
        setFieldValue("sender_fax", "");
        setFieldValue("sender_email", "");
        setFieldValue("sender_url", "");
        setFieldValue("sender_bank", "");
        setFieldValue("sender_logo", "");
        setFieldValue("sender_backaddress_separator", ", ");
        setFieldValue("my_reference", "");
        syncSignatureSuggestion();
    };

    const fillSampleLetter = () => {
        const today = new Date().toISOString().slice(0, 10);

        setAutofillMode(signatureField, false);
        setAutofillMode(filenameAddresseeField, false);

        setFieldValue("sender_title", "Dr.");
        setFieldValue("sender_first_name", "Albert");
        setFieldValue("sender_last_name", "Marks");
        setFieldValue("sender_extra", "2. Etage");
        setFieldValue("sender_street", "Stammheimer Str.");
        setFieldValue("sender_street_number", "94");
        setFieldValue("sender_postal_code", "50735");
        setFieldValue("sender_city", "Köln");
        setFieldValue("sender_phone", "0221 123456");
        setFieldValue("sender_mobile_phone", "0171 2345678");
        setFieldValue("sender_fax", "0221 654321");
        setFieldValue("sender_email", "albert.marks@example.com");
        setFieldValue("sender_url", "https://example.com");
        setFieldValue("sender_bank", "IBAN DE21 87654321 13456789\nBIC ABCDDEFFXXX");
        setFieldValue("sender_logo", "");
        setFieldValue("sender_backaddress_separator", ", ");
        setFieldValue("my_reference", "AM-2026-001");

        setFieldValue("recipient_title", "Herr");
        setFieldValue("recipient_first_name", "Hans");
        setFieldValue("recipient_last_name", "Schmitt");
        setFieldValue("recipient_extra", "Personalabteilung");
        setFieldValue("recipient_street", "Hauptstraße");
        setFieldValue("recipient_street_number", "5");
        setFieldValue("recipient_postal_code", "54321");
        setFieldValue("recipient_city", "Köln");
        setFieldValue("your_reference", "HS-2026-002");
        setFieldValue("your_mail", "12.05.2026");
        setFieldValue("customer", "4711");
        setFieldValue("invoice", "R-2026-88");

        setFieldValue("letter_title", "Mahnung");
        setFieldValue("subject", "Testbrief zur Layoutkontrolle");
        setFieldValue("subject_separator", ": ");
        setFieldValue("opening", "Sehr geehrter Herr Schmitt,");
        setFieldValue(
            "body",
            "hiermit erhalten Sie einen vollständigen Testbrief.\nBitte prüfen Sie alle Adress-, Referenz- und Datumsfelder.\n\nDies ist ein zweiter Absatz zur Prüfung des Absatzabstands."
        );
        setFieldValue("closing", "Mit freundlichen Grüßen");
        setFieldValue("ps", "Bitte bestätigen Sie den Erhalt.");
        setFieldValue("cc_separator", "Verteiler");
        setFieldValue("cc", "Frau Beispiel\nAblage");
        setFieldValue("encl_separator", "Anlagen");
        setFieldValue("encl", "Vertrag\nRechnungskopie");

        setFieldValue("place", "Köln");
        setFieldValue("place_separator", ", ");
        setFieldValue("date_iso", today);

        syncSignatureSuggestion();
        syncFilenameSuggestion();
        syncFilenamePreview();
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

    if (fillAlbertMarksButton) {
        fillAlbertMarksButton.addEventListener("click", fillAlbertMarks);
    }

    if (fillSampleLetterButton) {
        fillSampleLetterButton.addEventListener("click", fillSampleLetter);
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
