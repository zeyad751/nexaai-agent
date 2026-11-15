import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// The agent writes markdown: headings, lists, tables, bold. Raw HTML in answers is NOT
// rendered (react-markdown's default), so an answer can never inject markup.

// Rehype plugin: wrap project IDs (PRJ-001 ... PRJ-040) in <mark> so they stand out,
// except inside code. Walks the HTML tree and splits matching text nodes.
const PROJECT_ID = /PRJ-\d{3}/g;

function highlightProjectIds() {
  const visit = (node) => {
    if (!node.children || node.tagName === "code" || node.tagName === "pre") return;
    const next = [];
    for (const child of node.children) {
      if (child.type !== "text" || !PROJECT_ID.test(child.value)) {
        PROJECT_ID.lastIndex = 0;
        visit(child);
        next.push(child);
        continue;
      }
      PROJECT_ID.lastIndex = 0;
      let last = 0;
      for (const match of child.value.matchAll(PROJECT_ID)) {
        if (match.index > last) next.push({ type: "text", value: child.value.slice(last, match.index) });
        next.push({
          type: "element",
          tagName: "mark",
          properties: { className: ["project-id"] },
          children: [{ type: "text", value: match[0] }],
        });
        last = match.index + match[0].length;
      }
      if (last < child.value.length) next.push({ type: "text", value: child.value.slice(last) });
    }
    node.children = next;
  };
  return (tree) => visit(tree);
}

// The agent sometimes writes formulas in LaTeX (\[ ... \]). Rather than ship a math
// renderer, turn the simple cases it uses into readable plain text.
function tidyFormulas(text) {
  const clean = (expr) =>
    expr
      .replace(/\\text\{([^}]*)\}/g, "$1")
      .replace(/\\times/g, "×")
      .replace(/\\div/g, "÷")
      .replace(/\\%/g, "%")
      .replace(/\{,\}/g, ",")
      .replace(/\\,/g, " ")
      .replace(/\\left|\\right/g, "")
      .replace(/\s+/g, " ")
      .trim();
  return text
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, expr) => `\n\n> ${clean(expr)}\n\n`)
    .replace(/\\\(([\s\S]*?)\\\)/g, (_, expr) => clean(expr));
}

const components = {
  a: ({ node, ...props }) => <a {...props} target="_blank" rel="noopener noreferrer" />,
  table: ({ node, ...props }) => (
    <div className="table-scroll">
      <table {...props} />
    </div>
  ),
};

export default function Markdown({ children }) {
  return (
    <div className="prose">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[highlightProjectIds]} components={components}>
        {tidyFormulas(children || "")}
      </ReactMarkdown>
    </div>
  );
}
