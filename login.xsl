<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" indent="yes"/>

    <xsl:template match="/">
        <html>
        <head>
            <title><xsl:value-of select="loginPage/form/title"/></title>
            <style>
                *{margin: 0;padding: 0;box-sizing: border-box;font-family: sans-serif;}
                body {width: 100vw;height: 100vh;display: flex;align-items: center;justify-content: center;}
                form {background-color: rgba(0, 0, 0, 0.5);height: 550px;width: 500px;
                      display: flex;align-items: center;justify-content: center;
                      flex-direction: column;border-radius: 15px;}
                h2 {color: aliceblue;text-transform: uppercase;padding: 10px 0;font-size: 2em;}
                .form-group {border-bottom: 3px solid white;width: 330px;margin: 30px 0;}
                .form-group input {width: 100%;height: 40px;background-color: transparent;
                                   border: none;outline: none;color: #fff;}
                p {margin-top: 10px;color: white;text-align: center;padding: 10px;}
                button {border: none;transition: background-color 1s ease;height: 45px;
                        width: 70%;font-size: 1.5em;text-transform: uppercase;border-radius: 20px;}
                button:active {background-color: dodgerblue;}
            </style>
        </head>
        <body>
            <form>
                <h2><xsl:value-of select="loginPage/form/title"/></h2>
                <xsl:for-each select="loginPage/form/fields/field">
                    <div class="form-group">
                        <input type="{type}" placeholder="{placeholder}"/>
                    </div>
                </xsl:for-each>
                <p>
                    <input type="checkbox"/><xsl:value-of select="loginPage/form/options/checkbox"/>
                    <a href="#"><xsl:value-of select="loginPage/form/options/link"/></a>
                </p>
                <button type="submit"><xsl:value-of select="loginPage/form/button"/></button>
                <p>
                    <xsl:value-of select="loginPage/form/register/message"/>
                    <a href="{loginPage/form/register/link}">Register</a>
                </p>
            </form>
        </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
