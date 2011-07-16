<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
		xmlns:mmax="org.eml.MMAX2.discourse.MMAX2DiscourseLoader"
		xmlns:POS="www.eml.org/NameSpaces/POS"
		xmlns:NER="www.eml.org/NameSpaces/NER"
		xmlns:sentences="www.eml.org/NameSpaces/sentences">

<xsl:output method="text" indent="no" omit-xml-declaration="yes"/>
<xsl:strip-space elements="*"/>

<xsl:template match="words">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="word">
 <xsl:value-of select="mmax:registerDiscourseElement(@id)"/>
  <xsl:apply-templates select="mmax:getStartedMarkables(@id)" mode="opening"/>
  <xsl:value-of select="mmax:setDiscourseElementStart()"/>
   <xsl:apply-templates/>
  <xsl:value-of select="mmax:setDiscourseElementEnd()"/>
  <xsl:apply-templates select="mmax:getEndedMarkables(@id)" mode="closing"/>
<xsl:text> </xsl:text>
</xsl:template>


<xsl:template match="POS:markable" mode="opening">
 <xsl:if test="mmax:startsMarkableFromLevel(@id, @mmax_level, 'POS')=false">
 <xsl:text>
	</xsl:text> <!-- This is a tab character -->
 </xsl:if>
 <xsl:value-of select="mmax:addLeftMarkableHandle(@mmax_level, @id, '[')"/>
</xsl:template>

<xsl:template match="POS:markable" mode="closing">
  <xsl:value-of select="mmax:addRightMarkableHandle(@mmax_level,@id,string-length(@tag)+1,1)"/>
  <xsl:text>]</xsl:text>
  <xsl:value-of select="mmax:startSubscript()"/>
  <xsl:value-of select="@tag"/>
  <xsl:value-of select="mmax:endSubscript()"/>
</xsl:template>

<xsl:template match="NER:markable" mode="opening">
 <xsl:if test="mmax:startsMarkableFromLevel(@id, @mmax_level, 'NER')=false">
 <xsl:text>
	</xsl:text> <!-- This is a tab character -->
 </xsl:if>
 <xsl:value-of select="mmax:addLeftMarkableHandle(@mmax_level, @id, '[')"/>
</xsl:template>

<xsl:template match="NER:markable" mode="closing">
  <xsl:value-of select="mmax:addRightMarkableHandle(@mmax_level,@id,string-length(@tag)+1,1)"/>
  <xsl:text>]</xsl:text>
  <!--
  <xsl:value-of select="mmax:startSubscript()"/>
  <xsl:value-of select="@tag"/>
  <xsl:value-of select="mmax:endSubscript()"/>
  -->
</xsl:template>

<xsl:template match="sentences:markable" mode="closing">
  <xsl:text>
  </xsl:text>
  <xsl:text>
  </xsl:text>
</xsl:template>

</xsl:stylesheet>
