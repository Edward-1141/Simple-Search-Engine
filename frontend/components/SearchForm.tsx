import Form from 'next/form';
import AdvanceSearchOption from '@/components/AdvanceSearchOption';

export default function SearchForm({ query }: { query?: string }) {

  return (
    <Form action="/" scroll={false}>
      <div className="search-form">
        <input
          name="query"
          defaultValue={query}
          className="search-input"
          placeholder="Search for anything..."
        />

        <div className="flex gap-2 items-center">
          <button type="submit" className="search-btn text-white">
            🔍
          </button>
        </div>
      </div>

      < AdvanceSearchOption />
    </Form>
  )
}