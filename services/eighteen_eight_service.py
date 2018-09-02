# coding=utf-8
import requests


class EighteenEightService(object):
    BASE_URL = 'https://188bet.website'

    @staticmethod
    def __get_match_slug(e):
        dummy = e['dummy_match'] or {}
        return dummy.get('game', {}).get('slug')

    @staticmethod
    def __get_new_odds(odds):
        ret = dict(
            odd_name=odds['n'],
            odd_key=odds['mn'],
            odds=dict((o[0], float(o[2])) for o in odds['o'])
        )
        return ret

    @staticmethod
    def __get_odds(odds):
        ml = odds.get('ml', [])
        if len(ml) != 4:
            ml_res = {}
        else:
            ml_res = dict(
                home_team=float(ml[1]),
                away_team=float(ml[3]),
            )
        # TODO: ah
        return dict(ml=ml_res)

    @classmethod
    def __format_child_event(cls, e):
        ret = dict()
        ret['odds'] = cls.__get_odds(e.pop('odds', {}))
        ret['new_odds'] = map(cls.__get_new_odds, e.pop('new_odds', []))
        ret.update(e)
        return ret

    @classmethod
    def __format_match(cls, m):
        dummy = m['dummy_match'] or {}
        ret = dict(
            match_id=dummy['id'],
            stage_id=dummy['stage_round']['stage_format']['stage']['tournament']['id'],
            stage_name=dummy['stage_round']['stage_format']['stage']['tournament']['name'],
            stage_shorthandle=dummy['stage_round']['stage_format']['stage']['tournament']['shorthandle'],
        )
        events = m['events'] or []
        if not events:
            ret['event'] = {}
        else:
            event = events[0]
            ret_event = dict()
            ret_event['odds'] = cls.__get_odds(event.pop('odds', {}))
            ret_event['new_odds'] = map(cls.__get_new_odds, event.pop('new_odds', []))
            ret_event['child_events'] = map(cls.__format_child_event, event.pop('child_events', []))
            ret_event.update(event)
            ret['event'] = ret_event

        return ret

    @classmethod
    def get_all_matches(cls):
        uri = '/api/call.php?path=all/client-matches/1?type=1'
        url = cls.BASE_URL + uri
        try:
            data = requests.get(url).json()
        except Exception as e:
            print e
            return {}

        if not data.get('status') == 'success':
            return {}

        further_raw = [match for match in data['further'] if cls.__get_match_slug(match) == 'lol']
        in_play_raw = [match for match in data['inPlay'] if cls.__get_match_slug(match) == 'lol']
        further_format = map(cls.__format_match, further_raw)
        in_play_format = map(cls.__format_match, in_play_raw)

        return further_format, in_play_format

    @classmethod
    def get_match_detail(cls, match_id):
        uri = '/api/call.php?path=lol/match/client-odds/{match_id}/1?type=1'.format(match_id=match_id)
        url = cls.BASE_URL + uri
        try:
            data = requests.get(url).json()
        except Exception as e:
            print e
            return {}
        return data

