# SkillShelf

Open-source AI skill catalog for ecommerce teams. Every skill is a structured workflow you can load into Claude, ChatGPT, or any AI tool that supports the [Agent Skills](https://agentskills.io) format.

**[Browse the catalog on skillshelf.ai](https://skillshelf.ai)**

## What is a skill?

A skill is a set of instructions that tells an AI model what to do, what format to follow, and what good output looks like. Instead of writing a detailed prompt from scratch each time, you load a skill and get consistent, production-ready results.

Each skill is a folder containing a `SKILL.md` file (the core instructions) and optionally a `skillshelf.yaml` sidecar file (catalog metadata), examples, and supporting files.

## Using a skill

1. Browse the [skill catalog](https://skillshelf.ai/) or look through the `skills/` directory in this repo
2. Open the skill's `SKILL.md` file
3. Copy the contents into Claude, ChatGPT, or your preferred AI tool
4. Follow the skill's instructions with your own input data

You can also install skills via the CLI:

```bash
npx skills add timctfl/skillshelf -s brand-voice-extractor
```

## Skill directory structure

```
skills/
  brand-voice-extractor/
    SKILL.md              # Core instructions (required)
    skillshelf.yaml       # SkillShelf catalog metadata
    references/           # Example outputs, glossaries, supporting docs
      example-output.md
      glossary.md
  write-positioning-overview/
    SKILL.md
    skillshelf.yaml
    references/
      example-positioning-brief.md
```

See the existing skills in `skills/` for complete examples of what a finished skill looks like.

## Creating a skill

There are two paths:

**Conversational.** Open Claude or ChatGPT and describe the workflow you want to turn into a skill. The model will generate a properly structured `SKILL.md` for you. See the [full guide on skillshelf.ai](https://skillshelf.ai/learn/how-to-create-a-skill/) for a step-by-step walkthrough.

**Manual.** Write a `SKILL.md` file by hand following the [SKILL.md specification](skillmd-specs.md). The [Skill Authoring Guide](skill-authoring-guide.md) covers input design, output structure, example conventions, and quality standards.

## Submitting a skill

**Website.** Go to [skillshelf.ai/submit](https://skillshelf.ai/submit/) and upload your `.skill` or `.zip` file. The site opens a pull request on your behalf.

**GitHub.** Fork this repo, add your skill under `skills/your-skill-name/`, and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full process and requirements.

Every skill on SkillShelf goes through a certification review before it is published. All accepted skills are published under the Apache 2.0 license.

## Reference

- [SKILL.md Specification](skillmd-specs.md) -- format, frontmatter fields, validation rules
- [Skill Authoring Guide](skill-authoring-guide.md) -- best practices for writing effective skills
- [Glossary Specification](glossary-specification.md) -- how to write glossaries for downstream skill consumption
- [Contributing Guide](CONTRIBUTING.md) -- submission process, PR requirements, metadata reference
- [Agent Skills open standard](https://agentskills.io) -- the cross-platform format SkillShelf skills are built on

## License

Skills and documentation are published under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license.

Built and maintained by [Cartful](https://cartful.com).
