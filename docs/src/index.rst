**PyMuPDF4LLM** documentation is now found on https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/




.. raw:: html

    <p>You will be redirected <time><strong id="seconds">in 3 seconds.</strong></time></p>

    <script>

        var el = document.getElementById('seconds'),
        total = 3,
        timeinterval = setInterval(function () {
            total = --total;

            var printable = "in " + total.toString() + " seconds.";

            if (total==1) {
                printable = "in " + total.toString()  + " second.";
            }
            else if (total == 0) {
                printable = " now!";
            }

            el.textContent = printable;
            if (total <= 0) {
                clearInterval(timeinterval);
                window.location = 'https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/';
            }
        }, 1000);


    </script>

