import SearchForm from '@/components/SearchForm';
import SearchResults from '@/components/SearchResults';
import { SearchResult, SearchOptions } from '@/types/search';

type SearchParams = Partial<{ query: string } & SearchOptions>;

export default async function Page(props: {
  searchParams: Promise<SearchParams>;
}) {
  const searchParams = await props.searchParams
  const query = searchParams.query as string

  const params = new URLSearchParams(
    searchParams as Record<string, string>
  )
  // console.log(params.toString())
  const response = await fetch(`http://127.0.0.1:8080/api/search?${params}`)
  const data = await response.json()
  // console.log(data)

  return (
    <div className="max-w-7xl mx-auto px-4">
      <SearchForm query={query} />
      <SearchResults results={data.results} searchTime={data.time} />
    </div>
  );
}