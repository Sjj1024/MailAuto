import re

html = """

<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<body style="word-wrap: break-word; -webkit-nbsp-mode: space; line-break: after-white-space;" class="">Dear Sir,
<div class=""><br class=""></div>
<div class="">Please check it still has problem<br class="">
    <div><br class="">
        <blockquote type="cite" class="">
            <div class="">On Jan 19, 2025, at 5:56 PM, Sales Center &lt;<a href="mailto:info@swimming.com" class="">info@swimming.com</a>&gt;
                wrote:
            </div>
        </blockquote>
        <blockquote type="cite" class=""><br class="Apple-interchange-newline">
            <div class="">
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8" class="">
                <div style="word-wrap: break-word; -webkit-nbsp-mode: space; line-break: after-white-space;" class="">
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" class="">
                    <div style="word-wrap: break-word; -webkit-nbsp-mode: space; line-break: after-white-space;"
                         class="">
                        <div class="">Dear Sir,</div>
                        <div class=""><br class=""></div>
                        <div class="">Please provide a detailed shipping address. We will check the shipping cost and
                            forward your request to our sales department for a quotation
                        </div>
                        <div class=""><br class=""></div>
                        <div class=""><br class="">
                            <blockquote type="cite" class="">
                                <div class="">On Nov 22, 2024, at 10:06 PM, Info Kiconcerts &lt;<a
                                        href="mailto:info@kiconcerts.com" class="">info@kiconcerts.com</a>&gt; wrote:
                                </div>
                                <br class="Apple-interchange-newline">
                                <div class="">
                                    <div class="WordSection1"
                                         style="page: WordSection1; caret-color: rgb(0, 0, 0); font-family: Helvetica; font-size: 12px; font-style: normal; font-variant-caps: normal; font-weight: normal; letter-spacing: normal; text-align: start; text-indent: 0px; text-transform: none; white-space: normal; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration: none;">
                                        <div style="margin: 0in; font-size: 12pt; font-family: Aptos, sans-serif;"
                                             class=""><span style="font-size: 11pt; font-family: Verdana, sans-serif;"
                                                            class="">Thanks<o:p class=""></o:p></span></div>
                                        <div style="margin: 0in; font-size: 12pt; font-family: Aptos, sans-serif;"
                                             class=""><span style="font-size: 11pt; font-family: Verdana, sans-serif;"
                                                            class=""><o:p class="">&nbsp;</o:p></span></div>
                                        <div style="margin: 0in; font-size: 12pt; font-family: Aptos, sans-serif;"
                                             class=""><span style="font-size: 11pt; font-family: Verdana, sans-serif;"
                                                            class="">Can you please tell me the price points of the various models/options?<o:p
                                                class=""></o:p></span></div>
                                        <div style="margin: 0in; font-size: 12pt; font-family: Aptos, sans-serif;"
                                             class=""><span style="font-size: 11pt; font-family: Verdana, sans-serif;"
                                                            class=""><o:p class="">&nbsp;</o:p></span></div>
                                        <div style="margin: 0in; font-size: 12pt; font-family: Aptos, sans-serif;"
                                             class=""><span style="font-size: 11pt; font-family: Verdana, sans-serif;"
                                                            class="">Thanks</span></div>
                                        <div id="mail-editor-reference-message-container" class="">
                                            <div class="">
                                                <div class="">
                                                    <div style="border-style: solid none none; border-top-width: 1pt; border-top-color: rgb(181, 196, 223); padding: 3pt 0in 0in;"
                                                         class=""><p class="MsoNormal"
                                                                     style="margin: 0in 0in 12pt; font-size: 12pt; font-family: Aptos, sans-serif;">
                                                        <span style="" class=""><b class="">To:<span
                                                                class="Apple-converted-space">&nbsp;</span></b>Info Kiconcerts &lt;<a
                                                                href="mailto:info@headfirst.com" class="">info@headfirst.com</a>&gt;<span
                                                                style="font-size: 12pt;" class="">Hello,</span></span>
                                                    </p></div>
                                                    <p class="MsoNormal"
                                                       style="margin: 0in 0in 12pt; font-size: 12pt; font-family: Aptos, sans-serif;">
                                                        <br class=""><br class="">Powerful 500W Motor Fat Tires for Any
                                                        Terrain<br class="">Our electric bike comes with a 500W motor,
                                                        delivering an impressive 66.6NM of torque.<span
                                                            class="Apple-converted-space">&nbsp;</span><br class="">This
                                                        gives you plenty of power to ride at a top speed of 28 mph.
                                                        Paired with 26” x 4.0 anti-skidding fat tires, this bike is<span
                                                            class="Apple-converted-space">&nbsp;</span><br class="">built
                                                        to handle any terrain – from sandy beaches and snowy trails to
                                                        gravel paths and mountainous roads. Enjoy superior<span
                                                            class="Apple-converted-space">&nbsp;</span><br class="">grip,
                                                        stability, and a smooth ride wherever you go.<br class=""><br
                                                            class="">With a 48V 15AH removable lithium-ion battery, our
                                                        electric bike ensures long-lasting power for your
                                                        adventures.<span class="Apple-converted-space">&nbsp;</span><br
                                                            class="">You can expect a range of 30-35 miles in pure
                                                        electric mode, and up to 55-60 miles in Pedal Assist System
                                                        (PAS) mode,<span class="Apple-converted-space">&nbsp;</span><br
                                                            class="">depending on your weight, riding style, and
                                                        terrain. Charging time is about 6.5 hours,<span
                                                            class="Apple-converted-space">&nbsp;</span><br class="">and
                                                        the battery can be charged on or off the bike for your
                                                        convenience.<br class=""><br class="">For more information or to
                                                        proceed with your purchase, please don't hesitate to contact us.<span
                                                            class="Apple-converted-space">&nbsp;</span><br class="">To
                                                        calculate the shipping cost, we will need your delivery address.
                                                        We look forward to assisting you.<br class=""><br class=""><br
                                                            class=""></p></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </blockquote>
                        </div>
                        <br class=""></div>
                </div>
            </div>
        </blockquote>
    </div>
    <br class=""></div>
</body>
</html>
"""

result = re.split(r'</?body[^>]*>', html)

print(result)
