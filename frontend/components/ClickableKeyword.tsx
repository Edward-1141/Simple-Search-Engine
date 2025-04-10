'use client';

import { useRouter, useSearchParams } from "next/navigation";

const ClickableKeyword = ({ keyword, freq }: { keyword: string; freq: number }) => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const handleClick = (e: React.MouseEvent) => {
        e.preventDefault();
        const form = document.querySelector('form');

        if (form) {
            const queryInput = form.querySelector('input[name="query"]') as HTMLInputElement;
            if (queryInput) {
                queryInput.value = keyword;
            }
            form.requestSubmit();
        } else {
            const params = new URLSearchParams(searchParams.toString());
            params.set("query", keyword);
            router.push(`/search?${params.toString()}`);
        }
    };

    return (
        <div
            onClick={handleClick}
            className="px-2 py-1 bg-gray-100 rounded-full text-sm cursor-pointer hover:underline hover:bg-gray-200"
        >
            {keyword} ({freq})
        </div>
    );
};

export default ClickableKeyword;