import Checkbox from "@/components/CheckBox"
import { SearchParams } from '@/types/search';

const AdvanceSearchOption = ({ searchParams }: { searchParams?: SearchParams }) => {
  return (
    <details className="mt-4 mx-4">
      <summary className="cursor-pointer">
        <span className="text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold hover:underline">
          Advance Search Options
        </span>
      </summary>
      <div className="mt-4 mx-4">
        <Checkbox label="PageRank" inputName="page-rank" defaultChecked={searchParams?.["page-rank"] ?? true} />
        <Checkbox label="Match in Title" inputName="match-in-title" defaultChecked={searchParams?.["match-in-title"] || false} />

        <label className="flex items-center mt-4">
          <div className="text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold">
            Phrase Search Otions:
          </div>
          <select name="phrase-search-options" className="cursor-pointer p-1 border rounded-md ml-3 text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold" defaultValue={searchParams?.["phrase-search-options"] ?? 0}>
            <option value="0" className="ml-3 text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold">ignore stopwords</option>
            <option value="1" className="ml-3 text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold">with stopwords</option>
            <option value="2" className="ml-3 text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold">exact match (without stemming)</option>
          </select>
        </label>
        <label className="flex items-center mt-4">
          <div className="text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold">
            Phrase Search Distance:
          </div>
          <input
            type="number"
            name="phrase-search-distance"
            defaultValue={searchParams?.["phrase-search-distance"] ?? 1}
            className="p-0.5 border rounded-md ml-3 text-gray-700 group-hover:text-blue-500 transition-colors duration-300 font-bold"
          />
        </label>

      </div>
    </details>
  )
}

export default AdvanceSearchOption