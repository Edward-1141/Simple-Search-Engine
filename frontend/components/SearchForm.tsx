import Form from 'next/form';
import AdvanceSearchOption from '@/components/AdvanceSearchOption';
import { SearchParams } from '@/types/search';

export default function SearchForm( {searchParams}: { searchParams?: SearchParams }) {

  return (
    <Form action="/search" scroll={false}>
      <div className="search-form">
        <input
          name="query"
          defaultValue={searchParams?.query || "" }
          className="search-input"
          placeholder="Search for anything..."
        />

        <div className="flex gap-2 items-center">
          <button type="submit" className="search-btn text-white">
            🔍
          </button>
        </div>
      </div>

      < AdvanceSearchOption searchParams={searchParams || {}} />
    </Form>
  )
}