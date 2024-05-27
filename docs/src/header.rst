.. |PyMuPDF| raw:: html

    <cite>PyMuPDF</cite>

.. |PDF| raw:: html

    <cite>PDF</cite>

.. |Markdown| raw:: html

    <cite>Markdown</cite>


.. raw:: html

    <style>

        #languageToggle {
            float: right;
            width:auto;
            margin:8px 10px 0;
        }

        #button-select-en {
            padding: 5px 10px;
            background-color: #fff;
            border: 1px solid #000;
            border-radius: 10px 0 0 10px;
            font-size: 14px;
        }

        #button-select-ja {
            padding: 5px 10px;
            background-color: #fff;
            border: 1px solid #000;
            border-radius: 0px 10px 10px 0;
            border-left: 0;
            font-size: 14px;
        }

        #button-select-en , #button-select-ja, #button-select-en:hover , #button-select-ja:hover  {
            color: #fff;
            text-decoration: none;
        }

        @media all and (max-width : 375px)  {
            #button-select-en , #button-select-ja {
                font-size: 11px;
            }
        }

    </style>

    <div id="languageToggle"><span><a id="button-select-en" href="javaScript:changeLanguage('en')">English</a></span><span><a id="button-select-ja" href="javaScript:changeLanguage('ja')">日本語</a></span></div>
    <div style="clear:both"></div>


    <script>
        // highlightSelectedLanguage

        if (document.getElementsByTagName('html')[0].getAttribute('lang')=="ja") {
            document.getElementById("button-select-ja").style.backgroundColor = "#ff6600";
            document.getElementById("button-select-en").style.color = "#000";
        } else {
            document.getElementById("button-select-en").style.backgroundColor = "#ff6600";
            document.getElementById("button-select-ja").style.color = "#000";
        }


        var url_string = window.location.href;
        var a = document.getElementById('feedbackLinkTop');
        a.setAttribute("href", "https://artifex.com/contributor/feedback.php?utm_source=rtd-pymupdf&utm_medium=rtd&utm_content=header-link&url="+url_string);

        function changeLanguage(lang) {
            var new_url;

            if (lang == "en") {
                new_url = url_string.replace("/ja/", "/en/");
            } else {
                new_url = url_string.replace("/en/", "/ja/");
            }

            window.location.replace(new_url);
        }

    </script>

