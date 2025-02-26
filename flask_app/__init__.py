import sys
import os
import time
from datetime import date, datetime
from datetime import time as Time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from flask import Flask, jsonify
from flask import request
from flask_cors import CORS

from Score import SearchEngine

RESULTS_SHOWN = 50

db_path = os.path.join('db/spider_test.db')
search_engine = SearchEngine(db_path, title_weight=3.0)

def serialize_search_results(results):
    serialized_results = []
    for r in results:
        # Create a copy of the result dict
        result = r.copy()
        # Convert sets to lists for JSON serialization
        if 'word_pos' in result:
            result['word_pos'] = {k: list(v) for k, v in result['word_pos'].items()}
        if 'title_word_pos' in result:
            result['title_word_pos'] = {k: list(v) for k, v in result['title_word_pos'].items()}
        serialized_results.append(result)
    return serialized_results

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)  # Enable CORS for all routes
    
    @app.route("/api/search")
    def search():
        history = []
        options = {
            'phrase-search-options': '0',
            'match-in-title': None,
            'page-rank': True,
            'phrase-search-distance': 1,
            'skip-history': None,
            'exclude-words': None,
            'date-start': None,
            'time-start': None,
            'date-end': None,
            'time-end': None
        }
        
        if request.method == 'GET':
            if 'history' in request.cookies:
                history = request.cookies['history'].split(',')
            
            query = request.args.get('query')
            
            if len(request.args) > 1:
                for opt in options.keys():
                    options[opt] = None if request.args.get(opt) in [None, 'null', 'undefined', ''] else request.args.get(opt)
            
            print(options)

            if query:
                start = time.time()
                match_in_title = (options['match-in-title'] not in [None, 'false'])
                with_page_rank = (options['page-rank'] not in [None, 'false'])
                
                if options['phrase-search-options'] == '1':
                    raw_match_phrase, stem_for_raw = True, True
                elif options['phrase-search-options'] == '2':
                    raw_match_phrase, stem_for_raw = True, False
                else:
                    raw_match_phrase, stem_for_raw = False, False

                phrase_search_distance = int(options['phrase-search-distance']) if options['phrase-search-distance'] else 1

                if (match_in_title or raw_match_phrase) and '"' not in query:
                    query_quoted = f'"{query}"'
                    results, stemmed_query = search_engine.search(
                        query_quoted,
                        match_in_title=match_in_title,
                        raw_match_phrase=raw_match_phrase,
                        stem_for_raw=stem_for_raw,
                        phrase_search_distance=phrase_search_distance,
                        with_page_rank=with_page_rank
                    )
                else:
                    results, stemmed_query = search_engine.search(
                        query,
                        match_in_title=match_in_title,
                        raw_match_phrase=raw_match_phrase,
                        stem_for_raw=stem_for_raw,
                        phrase_search_distance=phrase_search_distance,
                        with_page_rank=with_page_rank
                    )

                results = results[:RESULTS_SHOWN]
                for r in results:
                    r['keywords'] = dict(list(r['keywords'].items())[:5])

                if any([options['date-start'], options['time-start'], options['date-end'], options['time-end']]):
                    date_start = date(1970,1,1) if options['date-start'] is None else date.fromisoformat(options['date-start'])
                    time_start = Time(0,0,0) if options['time-start'] is None else Time.fromisoformat(options['time-start'])
                    date_end = date.today() if options['date-end'] is None else date.fromisoformat(options['date-end'])
                    time_end = Time(23,59,59) if options['time-end'] is None else Time.fromisoformat(options['time-end'])
                    datetime_start = datetime.combine(date_start, time_start)
                    datetime_end = datetime.combine(date_end, time_end)
                    results = [r for r in results if r['last_modified'] >= datetime_start and r['last_modified'] <= datetime_end]

                
                results = serialize_search_results(results)

                end = time.time()
                
                # Update history if not skipped
                noskip = (options['skip-history'] is None)
                if noskip:
                    history = [h for h in history if h not in [query, '']]
                    history.append(query.replace(',', ' '))
                    history = history[-5:]

                # print(f"Query: {query}")
                # print(f"Results: {results[:5]}")
                # print(f"Time: {end-start}")
                # print(f"Options: {options}")
                # print(f"History: {history}")
                # print(f"Stemmed Query: {stemmed_query}")


                response = jsonify({
                    'query': query,
                    'results': results,
                    'time': "%.4f" % (end-start),
                    'options': options,
                    'history': history,
                    'stemmed_query': stemmed_query
                })

                if noskip:
                    response.set_cookie('history', ','.join(history))
                
                return response

        return jsonify({
            'history': history,
            'options': options
        })

    @app.route("/api/clear-history")
    def clear_history():
        del_item = request.args.get('item')
        response = jsonify({'success': True})
        
        if del_item:
            history = request.cookies.get('history', '').split(',')
            history = [h for h in history if h not in [del_item, '']]
            response.set_cookie('history', ','.join(history))
            if len(history) == 0:
                response.set_cookie('history', '', expires=0)
        else:
            response.set_cookie('history', '', expires=0)
            
        return response
    
    return app
