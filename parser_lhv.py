#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    RSS-voo sisendite parsimine
"""

from datetime import datetime, timedelta
import parsers_common
import rss_print


def getArticleListsFromHtml(pageTree, domain, maxArticleCount, getArticleBodies):
    """
    Meetod foorumi kõigi postituste nimekirja loomiseks
    """

    maxArticleCount = 15
    articlePostsCount = round(150 / maxArticleCount)  # set 0 for all posts

    articleTitles = parsers_common.xpath(pageTree, '//table[@class="grid zebra forum"]//tr/td[@class="title"]/a/@title')
    articleUrls = parsers_common.xpath(pageTree, '//table[@class="grid zebra forum"]//tr/td[@class="title"]/a/@href')

    articlePostsAuthors = []
    articlePostsDescriptions = []
    articlePostsImages = []
    articlePostsPubDates = []
    articlePostsTitles = []
    articlePostsUrls = []

    # teemade läbivaatamine
    for i in range(0, min(len(articleUrls), maxArticleCount)):
        if (articleUrls[i] == "/forum/free/121915"):  # Kalev Jaik võsafilosoofist majandusteadlane
            rss_print.print_debug(__file__, 'jätame Jaiki filosoofia vahele', 0)
            i += 1

        # teemalehe sisu hankimine
        if (getArticleBodies is True):
            articlePostsTree = parsers_common.getArticleData(domain, articleUrls[i] + '?listEventId=jumpToPage&listEventParam=100&pagesOfMaxSize=true', True)  # True teeb alati päringu

            articleLoopAuthors = parsers_common.xpath(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/p[@class="author"]/strong/a/text()')
            articleLoopIds = parsers_common.xpath(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/@href')
            articleLoopPubDates = parsers_common.xpath(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-header clear"]/div/p[@class="permalink"]/a/text()')
            articleLoopDescriptionsParents = parsers_common.xpath(articlePostsTree, '//ul[@class="forum-topic"]/li/div[@class="col2"]/div[@class="forum-content temporary-class"]')

            rss_print.print_debug(__file__, 'xpath parsimisel ' + str(len(articleLoopIds)) + " leid(u)", 1)

            # postituste läbivaatamine
            for j in range(max(0, len(articleLoopIds) - articlePostsCount), len(articleLoopIds)):
                rss_print.print_debug(__file__, 'teema postitus nr. ' + str(j + 1) + "/(" + str(len(articleLoopIds)) + ") on " + articleLoopIds[j], 2)

                # generate articlePostsUrls from articlePostsIds
                articlePostsUrls.append(articleUrls[i] + articleLoopIds[j])

                # author
                articlePostsAuthors.append(articleLoopAuthors[j])

                # description
                curArtDescriptionsChilds = parsers_common.stringify_children(articleLoopDescriptionsParents[j]) + " "
                curArtDescriptionsChilds = parsers_common.fixDrunkPost(curArtDescriptionsChilds)
                articlePostsDescriptions.append(curArtDescriptionsChilds)

                # timeformat magic from "15.01.2012 23:49" to datetime()
                curArtPubDate = articleLoopPubDates[j]
                curArtPubDate = curArtPubDate.strip()
                curArtPubDate = curArtPubDate.replace('Eile', (datetime.now() - timedelta(days=1)).strftime('%d.%m.%Y'))
                if len(curArtPubDate) < len("%d.%m.%Y %H:%M"):
                    curArtPubDate = datetime.now().strftime('%d.%m.%Y') + ' ' + curArtPubDate
                    rss_print.print_debug(__file__, "lisasime tänasele kellaajale kuupäeva: " + curArtPubDate, 3)
                curArtPubDate = parsers_common.rawToDatetime(curArtPubDate, "%d.%m.%Y %H:%M")
                articlePostsPubDates.append(curArtPubDate)

                # title
                articlePostsTitles.append(articleTitles[i] + " @" + domain)

    return {"articleAuthors": articlePostsAuthors,
            "articleDescriptions": articlePostsDescriptions,
            "articleImages": articlePostsImages,
            "articlePubDates": articlePostsPubDates,
            "articleTitles": articlePostsTitles,
            "articleUrls": articlePostsUrls,
           }
