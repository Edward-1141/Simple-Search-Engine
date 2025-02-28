import { SearchResult } from '@/types/search';
import ClickableKeyword from '@/components/ClickableKeyword';

interface SearchResultsProps {
  results: SearchResult[];
  searchTime: string;
}

export default function SearchResults({ results, searchTime }: SearchResultsProps) {
  if (!results) return null;
  if (!results.length) return null;

  return (
    <div className="mt-8">
      <p className="text-sm text-gray-600 mb-4">
        {results.length} results ({searchTime} seconds)
      </p>
      
      <div className="space-y-8">
        {results.map((result, index) => (
          <div key={index} className="border rounded-lg p-4 hover:shadow-lg transition">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-1 bg-blue-100 rounded text-sm">
                {result.score.toFixed(4)}
              </span>
              <a href={result.url} className="text-xl font-semibold text-blue-600 hover:underline">
                {result.title}
              </a>
            </div>
            
            <a href={result.url} className="text-sm text-gray-600 hover:underline">
              {result.url}
            </a>
            
            <p className="mt-2 text-sm text-gray-800">{result.body}</p>
            
            <div className="mt-2 text-sm text-gray-600">
              Last Modified: {result.last_modified} • Size: {result.size} bytes
            </div>
            
            <div className="mt-2 flex flex-wrap gap-2">
              {Object.entries(result.keywords).map(([keyword, freq]) => (
                <ClickableKeyword keyword={keyword} freq={freq} key={keyword} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}