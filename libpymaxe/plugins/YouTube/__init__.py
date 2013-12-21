# -*- coding: utf-8 -*-
import HTMLParser
import urllib2
import urllib
import datetime
import os
import json
import re
h = HTMLParser.HTMLParser()

FILE_TYPE_AUDIO = 0x01
FILE_TYPE_VIDEO = 0x02
_NO_DEFAULT = object()


class Plugin:
    def __init__(self):
        self.pluginName = 'YouTube Downloader'
        self.version = '1.0beta'
        self.author = 'Ovidiu D. Niţan'
        self.homepage = 'http://www.google.ro'
        self.update = 'http://www.google.com'
        self.matchurls = ['youtube.com']
        self.quality = 'medium'  # large, hd1080, hd720
        self.threaded_dnld = True

    def search(self, query):
        res = []
        print 'http://gdata.youtube.com/feeds/api/videos?q=' + urllib.quote(query) + '&alt=json'
        req = urllib2.Request('http://gdata.youtube.com/feeds/api/videos?q=' + urllib.quote(query) + '&alt=json')
        getdata = urllib2.urlopen(req)
        data = json.loads(getdata.read())
        results = data['feed']['entry']
        for entry in results:
            try:
                url = entry['link'][0]['href']
                title = entry['title']['$t']
                duration = str(datetime.timedelta(seconds=int(entry['media$group']['media$content'][0]['duration'])))[2:]
                res.append([FILE_TYPE_VIDEO, self.unescape(title), url, duration, False])
            except:
                pass
        return res

    def fileData(self, url):
        vcode = os.path.basename(url)
        try:
            gvcode = vcode.split('v=')
            gvcode = gvcode[1].split('&')
            vcode = gvcode[0]
        except:
            vcode = vcode
        url = 'http://www.youtube.com/watch?v=' + vcode
        req = urllib2.Request(url)
        getdata = urllib2.urlopen(req)
        data = getdata.read()
        gjson = data.split('ytplayer.config = ')
        gjson = gjson[1].split('};')
        json_data = json.loads(gjson[0] + '}')
        timp = str(datetime.timedelta(seconds=json_data['args']['length_seconds']))[2:]
        title = json_data['args']['title']
        itags = json_data['args']['url_encoded_fmt_stream_map'].split(',')
        qualities = {}
        for itag in itags:
            known_itags = ['5', '34', '35', '22', '37']
            itag_id_start = itag.split('itag=')[1]
            if '&' in itag_id_start:
                itag_id = itag_id_start.split('&')[0]
            else:
                itag_id = itag_id_start.split(',')[0]   # youtube is pissing me off

            if not itag_id in known_itags:
                continue

            if 'sig=' in itag:
                itag_sig = itag.split('sig=')[1][:81]
            else:
                itag_sig = self._decrypt_signature(itag.split('s=')[1].split('&')[0])

            itag_url = urllib.unquote(itag.split('url=')[1].split('&')[0])
            if ',' in itag_url:
                itag_url = itag_url.split(',')[0]

            if itag_id == '5':
                qualities['low'] = itag_url + '&signature=' + itag_sig
            if itag_id == '34':
                qualities['medium'] = itag_url + '&signature=' + itag_sig
            if itag_id == '35':
                qualities['large'] = itag_url + '&signature=' + itag_sig
            if itag_id == '22':
                qualities['hd720'] = itag_url + '&signature=' + itag_sig
            if itag_id == '37':
                qualities['hd1080'] = itag_url + '&signature=' + itag_sig
        downurl = self.select_quality(qualities)

        rq = urllib2.Request(downurl)
        gtdata = urllib2.urlopen(rq)
        contentlength = gtdata.info().getheader('Content-Length')
        data = {"url": url,
                "title": self.unescape(title),
                "length": timp,
                "type": FILE_TYPE_VIDEO,
                "fsize": contentlength,
                "downurl": downurl,
                "hiquality": False}
        return data

    def select_quality(self, qualities):
        q = ['hd1080', 'hd720', 'large', 'medium', 'low']
        if self.quality in qualities:
            return qualities[self.quality]
        for x in q:
            if qualities.has_key(x):
                return qualities[x]
        return qualities['medium']

    def unescape(self, s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        # this has to be last:
        s = s.replace("&amp;", "&")
        return s

    def _decrypt_signature(self, s):
        """Decrypt the key the two subkeys must have a length of 43"""
        """Source: youtube-dl project"""
        if len(s) == 93:
            return s[86:29:-1] + s[88] + s[28:5:-1]
        elif len(s) == 92:
            return s[25] + s[3:25] + s[0] + s[26:42] + s[79] + s[43:79] + s[91] + s[80:83]
        elif len(s) == 91:
            return s[84:27:-1] + s[86] + s[26:5:-1]
        elif len(s) == 90:
            return s[25] + s[3:25] + s[2] + s[26:40] + s[77] + s[41:77] + s[89] + s[78:81]
        elif len(s) == 89:
            return s[84:78:-1] + s[87] + s[77:60:-1] + s[0] + s[59:3:-1]
        elif len(s) == 88:
            return s[81:65:-1] + s[84] + s[64:60:-1] + s[65] + s[59:32:-1] + s[0] + s[31:0:-1]
        elif len(s) == 87:
            return s[6:27] + s[4] + s[28:39] + s[27] + s[40:59] + s[2] + s[60:]
        elif len(s) == 86:
            return s[80:72:-1] + s[16] + s[71:39:-1] + s[72] + s[38:16:-1] + s[82] + s[15::-1]
        elif len(s) == 85:
            return s[3:11] + s[0] + s[12:55] + s[84] + s[56:84]
        elif len(s) == 84:
            return s[78:70:-1] + s[14] + s[69:37:-1] + s[70] + s[36:14:-1] + s[80] + s[:14][::-1]
        elif len(s) == 83:
            return s[80:63:-1] + s[0] + s[62:0:-1] + s[63]
        elif len(s) == 82:
            return s[80:37:-1] + s[7] + s[36:7:-1] + s[0] + s[6:0:-1] + s[37]
        elif len(s) == 81:
            return s[56] + s[79:56:-1] + s[41] + s[55:41:-1] + s[80] + s[40:34:-1] + s[0] + s[33:29:-1] + s[34] + s[28:9:-1] + s[29] + s[8:0:-1] + s[9]
        elif len(s) == 80:
            return s[1:19] + s[0] + s[20:68] + s[19] + s[69:80]
        elif len(s) == 79:
            return s[54] + s[77:54:-1] + s[39] + s[53:39:-1] + s[78] + s[38:34:-1] + s[0] + s[33:29:-1] + s[34] + s[28:9:-1] + s[29] + s[8:0:-1] + s[9]

        else:
            raise ExtractorError(u'Unable to decrypt signature, key length %d not supported; retrying might work' % (len(s)))

    def _download_player(self, video_id):
        req = urllib2.urlopen('https://s.ytimg.com/yts/jsbin/html5player-{0}.js'.format(video_id))
        data = req.read()

    def _search_regex(self, pattern, string, name, default=_NO_DEFAULT, fatal=True, flags=0):
        """
        Perform a regex search on the given string, using a single or a list of
        patterns returning the first matching group.
        In case of failure return a default value or raise a WARNING or a
        RegexNotFoundError, depending on fatal, specifying the field name.
        """
        if isinstance(pattern, (str, compat_str, compiled_regex_type)):
            mobj = re.search(pattern, string, flags)
        else:
            for p in pattern:
                mobj = re.search(p, string, flags)
                if mobj: break

        if os.name != 'nt' and sys.stderr.isatty():
            _name = u'\033[0;34m%s\033[0m' % name
        else:
            _name = name

        if mobj:
            # return the first matching group
            return next(g for g in mobj.groups() if g is not None)
        elif default is not _NO_DEFAULT:
            return default
        elif fatal:
            raise RegexNotFoundError(u'Unable to extract %s' % _name)
        else:
            self._downloader.report_warning(u'unable to extract %s; '
                u'please report this issue on http://yt-dl.org/bug' % _name)
            return None

    def _parse_sig_js(self, jscode):
        funcname = self._search_regex(
            r'signature=([a-zA-Z]+)', jscode,
            u'Initial JS player signature function name')

        functions = {}

        def argidx(varname):
            return string.lowercase.index(varname)

        def interpret_statement(stmt, local_vars, allow_recursion=20):
            if allow_recursion < 0:
                raise ExtractorError(u'Recursion limit reached')

            if stmt.startswith(u'var '):
                stmt = stmt[len(u'var '):]
            ass_m = re.match(r'^(?P<out>[a-z]+)(?:\[(?P<index>[^\]]+)\])?' +
                             r'=(?P<expr>.*)$', stmt)
            if ass_m:
                if ass_m.groupdict().get('index'):
                    def assign(val):
                        lvar = local_vars[ass_m.group('out')]
                        idx = interpret_expression(ass_m.group('index'),
                                                   local_vars, allow_recursion)
                        assert isinstance(idx, int)
                        lvar[idx] = val
                        return val
                    expr = ass_m.group('expr')
                else:
                    def assign(val):
                        local_vars[ass_m.group('out')] = val
                        return val
                    expr = ass_m.group('expr')
            elif stmt.startswith(u'return '):
                assign = lambda v: v
                expr = stmt[len(u'return '):]
            else:
                raise ExtractorError(
                    u'Cannot determine left side of statement in %r' % stmt)

            v = interpret_expression(expr, local_vars, allow_recursion)
            return assign(v)

        def interpret_expression(expr, local_vars, allow_recursion):
            if expr.isdigit():
                return int(expr)

            if expr.isalpha():
                return local_vars[expr]

            m = re.match(r'^(?P<in>[a-z]+)\.(?P<member>.*)$', expr)
            if m:
                member = m.group('member')
                val = local_vars[m.group('in')]
                if member == 'split("")':
                    return list(val)
                if member == 'join("")':
                    return u''.join(val)
                if member == 'length':
                    return len(val)
                if member == 'reverse()':
                    return val[::-1]
                slice_m = re.match(r'slice\((?P<idx>.*)\)', member)
                if slice_m:
                    idx = interpret_expression(
                        slice_m.group('idx'), local_vars, allow_recursion-1)
                    return val[idx:]

            m = re.match(
                r'^(?P<in>[a-z]+)\[(?P<idx>.+)\]$', expr)
            if m:
                val = local_vars[m.group('in')]
                idx = interpret_expression(m.group('idx'), local_vars,
                                           allow_recursion-1)
                return val[idx]

            m = re.match(r'^(?P<a>.+?)(?P<op>[%])(?P<b>.+?)$', expr)
            if m:
                a = interpret_expression(m.group('a'),
                                         local_vars, allow_recursion)
                b = interpret_expression(m.group('b'),
                                         local_vars, allow_recursion)
                return a % b

            m = re.match(
                r'^(?P<func>[a-zA-Z]+)\((?P<args>[a-z0-9,]+)\)$', expr)
            if m:
                fname = m.group('func')
                if fname not in functions:
                    functions[fname] = extract_function(fname)
                argvals = [int(v) if v.isdigit() else local_vars[v]
                           for v in m.group('args').split(',')]
                return functions[fname](argvals)
            raise ExtractorError(u'Unsupported JS expression %r' % expr)

        def extract_function(funcname):
            func_m = re.search(
                r'function ' + re.escape(funcname) +
                r'\((?P<args>[a-z,]+)\){(?P<code>[^}]+)}',
                jscode)
            argnames = func_m.group('args').split(',')

            def resf(args):
                local_vars = dict(zip(argnames, args))
                for stmt in func_m.group('code').split(';'):
                    res = interpret_statement(stmt, local_vars)
                return res
            return resf

        initial_function = extract_function(funcname)
        return lambda s: initial_function([s])