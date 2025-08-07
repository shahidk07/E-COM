<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="/">
        <html lang="en">
            <head>
                <meta charset="UTF-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <title>Shahid Store</title>
                <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"/>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"/>
                <style>
                    body { background-image: url(back.jpeg); }
                    header { background: linear-gradient(45deg, #ff0c9e, #00ffff, #c30360); color: #fff; padding: 19px; text-align: center; }
                    header h1 { color: #fff; font-size: 3em; text-shadow: 0 0 5px hsl(263, 100%, 50%); }
                    .search { width: 700px; background: #f6f6f6; border-radius: 28px; display: flex; justify-content: center; }
                    nav ul { display: flex; justify-content: center; }
                    footer { background: #333; color: white; text-align: center; padding: 10px; }
                </style>
            </head>
            <body>
                <xsl:apply-templates select="website/header"/>
                <xsl:apply-templates select="website/main"/>
                <xsl:apply-templates select="website/footer"/>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="header">
        <header>
            <h1><xsl:value-of select="h1"/></h1>
            <nav>
                <ul>
                    <xsl:for-each select="nav/ul/li">
                        <li><a href="{a/@href}"><xsl:value-of select="a"/></a></li>
                    </xsl:for-each>
                </ul>
            </nav>
        </header>
    </xsl:template>

    <!-- Template for the main section -->
    <xsl:template match="main">
        <main>
            <div class="container">
                <div class="about-section">
                    <h2><xsl:value-of select="div/about-section/h2"/></h2>
                    <p><xsl:value-of select="div/about-section/p[1]"/></p>
                    <p><xsl:value-of select="div/about-section/p[2]"/></p>
                    <div class="mission">
                        <h3><xsl:value-of select="div/about-section/div/mission/h3"/></h3>
                        <p><xsl:value-of select="div/about-section/div/mission/p"/></p>
                    </div>
                </div>
            </div>
        </main>
    </xsl:template>

    <xsl:template match="footer">
        <footer>
            <div class="about">
                <h3><xsl:value-of select="div/about/h3"/></h3>
                <p><xsl:value-of select="div/about/p"/></p>
            </div>
            <div class="links">
                <h3><xsl:value-of select="div/links/h3"/></h3>
                <p><xsl:value-of select="div/links/p"/></p>
            </div>
            <div class="other">
                <h3><xsl:value-of select="div/other/h3"/></h3>
                <p><xsl:value-of select="div/other/p"/></p>
            </div>
        </footer>
    </xsl:template>

</xsl:stylesheet>
